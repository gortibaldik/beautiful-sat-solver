import logzero
import rq
import server.getters
import traceback

from contextlib import redirect_stderr, redirect_stdout
from satsolver.utils.check import check_assignment
from server.config import Config
from server.task_runner.benchmark import log_level_per_debug_level
from server.task_runner.utils import (
  ensure_storage_file_custom_run,
  retrieve_algorithm,
  retrieve_benchmark_filename,
  task_runner_start
)

def custom_run(
  file,
  algorithm_name,
  benchmark_name,
  entry_name,
  debug_level
):
  benchmark_filename = None
  try:
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    benchmark_filename = retrieve_benchmark_filename(
      benchmark_name,
      entry_name
    )
    if benchmark_filename is None:
      logzero.logger.warning(f"Benchmark with name: {benchmark_name} not found, EXITING!")
      return

    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)
    logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Entry: {entry_name} Log Level: {debug_level}")
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
      is_satisfiable="uuf" not in benchmark_filename,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    logzero.loglevel(Config.DEFAULT_LOGLEVEL)
    file.flush()
  except:
    if benchmark_filename is not None:
      logzero.logger.warning(f"Filename with error: {benchmark_filename}")
    logzero.logger.warning(traceback.format_exc())

def run_custom_input(
  algorithm_name=None,
  benchmark_name=None,
  entry_name=None,
  debug_level=None
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file_custom_run()
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        custom_run(
          f,
          algorithm_name,
          benchmark_name,
          entry_name,
          debug_level
        )
        logzero.logfile(None)
  job.meta['finished'] = True
  job.save_meta()

  return job

def task_runner_start_algorithm_on_custom_run(
  algorithm_name,
  benchmark_name,
  entry_name,
  debug_level
):
  return task_runner_start(
    'server.task_runner.custom_run.run_custom_input',
    algorithm_name=algorithm_name,
    benchmark_name=benchmark_name,
    entry_name=entry_name,
    debug_level=debug_level
  )
