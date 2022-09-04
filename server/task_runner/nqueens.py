import logzero
import rq
import server.getters
import traceback

from contextlib import redirect_stderr, redirect_stdout
from satsolver.utils.check import check_assignment
from server.config import Config
from server.task_runner.benchmark import log_level_per_debug_level
from server.task_runner.utils import (
  retrieve_algorithm,
  task_runner_start
)

def problem(
  get_problem_start_log,
  generate_dimacs_file,
  is_satisfiable,
  commit_f,
  file=None,
  algorithm=None,
  storage_file=None,
  debug_level=None,
  **kwargs
):
  benchmark_filename = None
  try:
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm} not found, EXITING!")
      return

    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)
    logzero.logger.warning(f"Algorithm: {algorithm}, {get_problem_start_log(**kwargs)}, Log Level: {debug_level}")
    benchmark_filename = generate_dimacs_file(generate_new=True, **kwargs)
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
      is_satisfiable=is_satisfiable(**kwargs),
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    save_model(result)

    logzero.loglevel(Config.DEFAULT_LOGLEVEL)
    file.flush()

    commit_f(
      algorithm=algorithm,
      storage_file=storage_file,
      avg_time=result["time"],
      stats=result["stats"],
      **kwargs
    )
    return result
  except:
    if benchmark_filename is not None:
      logzero.logger.warning(f"Filename with error: {benchmark_filename}")
    logzero.logger.warning(traceback.format_exc())

def benchmark_problem(
  get_problem_start_log,
  generate_dimacs_file,
  is_satisfiable,
  get_benchmark_start,
  get_benchmark_next,
  is_benchmark_finished,
  commit_f,
  **kwargs
):
  kwargs = get_benchmark_start(**kwargs)
  while True:
    result = problem(
      get_problem_start_log,
      generate_dimacs_file,
      is_satisfiable,
      commit_f,
      **kwargs
    )
    kwargs = get_benchmark_next(**kwargs)
    if is_benchmark_finished(result, **kwargs):
      break

def run_problem(
  get_problem_start_log,
  generate_dimacs_file,
  is_satisfiable,
  commit_f,
  ensure_storage_file,
  get_benchmark_start=None,
  get_benchmark_next=None,
  is_benchmark_finished=None,
  algorithm=None,
  debug_level=None,
  run_as_benchmark=False,
  **kwargs
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm)
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        if run_as_benchmark:
          benchmark_problem(
            get_problem_start_log,
            generate_dimacs_file,
            is_satisfiable,
            get_benchmark_start,
            get_benchmark_next,
            is_benchmark_finished,
            commit_f,
            file=f,
            algorithm=algorithm,
            storage_file=storage_file,
            debug_level=debug_level,
            **kwargs
          )
        else:
          problem(
            get_problem_start_log,
            generate_dimacs_file,
            is_satisfiable,
            commit_f,
            file=f,
            algorithm=algorithm,
            storage_file=storage_file,
            debug_level=debug_level,
            **kwargs
          )
        logzero.logfile(None)
  job.meta['finished'] = True
  job.save_meta()

  return job

def task_runner_start_algo_on_problem(
  get_problem_start_log,
  generate_dimacs_file,
  is_satisfiable,
  commit_f,
  ensure_storage_file,
  **kwargs
):
  return task_runner_start(
    'server.task_runner.nqueens.run_problem',
    get_problem_start_log=get_problem_start_log,
    generate_dimacs_file=generate_dimacs_file,
    is_satisfiable=is_satisfiable,
    commit_f=commit_f,
    ensure_storage_file=ensure_storage_file,
    **kwargs
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
