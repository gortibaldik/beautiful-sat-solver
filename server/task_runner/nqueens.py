import logzero
import rq
import server.getters
import traceback

from contextlib import redirect_stderr, redirect_stdout
from satsolver.task6 import generate_nqueens_dimacs
from satsolver.utils.check import check_assignment
from server.config import Config
from server.models.nqueens import create_n_commit_nqueens, create_nqueens
from server.task_runner.benchmark import log_level_per_debug_level
from server.task_runner.utils import (
  ensure_storage_file,
  retrieve_algorithm,
  task_runner_start
)

def nqueens(
  file,
  algorithm_name,
  n,
  storage_file,
  debug_level
):
  try:
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)
    logzero.logger.warning(f"Algorithm: {algorithm_name}, nqueens: N = {n} Log Level: {debug_level}")
    benchmark_filename = None
    benchmark_filename = generate_nqueens_dimacs(N=n)
    result = algo_module(
      input_file=benchmark_filename,
      debug=debug,
      warning=warning,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    file.flush()
    check_assignment(
      input_file=benchmark_filename,
      assignment_source=result["model"],
      debug=check_debug,
      warning=check_warning,
      read_from_file=False,
      is_satisfiable=int(n) != 3,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    save_model(result)

    logzero.loglevel(Config.DEFAULT_LOGLEVEL)
    file.flush()

    create_n_commit_nqueens(
      algorithm_name=algorithm_name,
      n=n,
      storage_file=storage_file,
      avg_time=result["time"],
      stats=result["stats"]
    )
    return result
  except:
    if benchmark_filename is not None:
      logzero.logger.warning(f"Filename with error: {benchmark_filename}")
    logzero.logger.warning(traceback.format_exc())

def nqueens_benchmark(
  f,
  algorithm_name,
  storage_file,
  debug_level,
  timeout
):
  n = 3
  while True:
    result = nqueens(
      f,
      algorithm_name,
      n,
      storage_file,
      debug_level
    )
    n += 1
    if result["time"] > timeout:
      break

def run_nqueens(
  algorithm_name=None,
  n=None,
  run_as_benchmark=False,
  timeout=None,
  debug_level=None
):
  timeout = int(timeout)
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, "__nqueens__")
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        if run_as_benchmark:
          nqueens_benchmark(
            f,
            algorithm_name,
            storage_file,
            debug_level,
            timeout
          )
        else:
          nqueens(
            f,
            algorithm_name,
            n,
            storage_file,
            debug_level
          )
        logzero.logfile(None)
  job.meta['finished'] = True
  job.save_meta()

  return job

def task_runner_start_algorithm_on_nqueens(
  algorithm,
  N,
  run_as_benchmark,
  timeout,
  debug_level
):
  return task_runner_start(
    'server.task_runner.nqueens.run_nqueens',
    algorithm_name=algorithm,
    n=N,
    run_as_benchmark=run_as_benchmark,
    timeout=timeout,
    debug_level=debug_level
  )

def save_model(result):
  if "model" not in result:
    return
  model = result["model"]
  if model is None:
    return
  array_to_write = []
  for variable, value in model.items():
    int_var = int(variable)
    if not value:
      int_var *= -1
    array_to_write.append(int_var)
  array_to_write = sorted(array_to_write, key=abs)
  job = rq.get_current_job()
  job.meta["model"] = array_to_write
  job.save_meta()
