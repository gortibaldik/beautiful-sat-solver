import os
import traceback
import logzero
import rq
import server.getters

from contextlib import redirect_stderr, redirect_stdout
from satsolver.utils.check import check_assignment
from satsolver.utils.stats import SATSolverStats
from server.config import Config
from server.models.job import create_n_commit_satjob
from server.task_runner.utils import (
  ensure_storage_file,
  retrieve_algorithm,
  retrieve_benchmark_filenames,
  task_runner_start
)

def init_cumulative_stats():
  return {
    "stats": SATSolverStats(),
    "time": 0,
    "total": 0,
  }

def update_cumulative_stats(
  *,
  cumulative_stats,
  result
):
  cumulative_stats["stats"].update(result["stats"])
  cumulative_stats["total"] += 1
  cumulative_stats["time"] += result["time"]

def avg_cumulative_stats(cumulative_stats):
  total = cumulative_stats["total"]
  cumulative_stats["stats"].divide(total)
  cumulative_stats["time"] /= total

def log_level_per_debug_level(debug_level):
  debug, info, warning = False, False, False
  if debug_level == "INFO":
    logzero.logger.info("Selected log level: INFO")
    info = True
  if debug_level == "DEBUG":
    logzero.logger.info("Selected log level: DEBUG")
    debug = True
  if debug_level == "WARNING":
    logzero.logger.info("Selected log level: WARNING")
    warning = True
  
  return debug, info, warning


def benchmark(file, algorithm_name, benchmark_name, debug_level):
  try:
    job = rq.get_current_job()
    job.meta["progress"] = 0
    job.save_meta()
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    benchmark_filenames = retrieve_benchmark_filenames(benchmark_name)
    if benchmark_filenames is None:
      logzero.logger.warning(f"Benchmark with name: {benchmark_name} not found, EXITING!")
      return

    total_number_of_benchmarks = len(benchmark_filenames)
    cumulative_stats = init_cumulative_stats()
    logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Log Level: {debug_level}")
    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)

    for i, filename in enumerate(benchmark_filenames):
      logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Entry: {filename} Log Level: {debug_level}")
      job.meta['progress'] = i * 100 / total_number_of_benchmarks
      job.save_meta()
      result = algo_module(
        input_file=filename,
        debug=debug,
        warning=warning,
        nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
      )
      check_assignment(
        input_file=filename,
        assignment_source=result["model"],
        debug=check_debug,
        warning=check_warning,
        read_from_file=False,
        is_satisfiable="uuf" not in filename,
        nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
      )
      logzero.loglevel(Config.DEFAULT_LOGLEVEL)
      if result is None:
        break
      update_cumulative_stats(
        cumulative_stats=cumulative_stats,
        result=result
      )
      file.flush()
    avg_cumulative_stats(cumulative_stats)
    logzero.logger.info(f"Stats: {cumulative_stats['stats']}; time: {cumulative_stats['time']}")
  except:
    if filename is not None:
      logzero.logger.warning(f"Filename with error: {filename}")
    logzero.logger.warning(traceback.format_exc())
    return None
  
  return cumulative_stats

def run_benchmark(
  algorithm_name=None,
  benchmark_name=None,
  debug_level=None,
  finished_meta_key="finished"
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, benchmark_name)
  if storage_file is None:
    job.meta['interrupted'] = True
    job.save_meta()
    return
  logzero.logger.info(f"Selected storage file: {storage_file}")
  job.meta[finished_meta_key] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        result = benchmark(f, algorithm_name, benchmark_name, debug_level)
        logzero.logfile(None)
  if result is None:
    result = init_cumulative_stats()
    job.meta['interrupted'] = True
  else:
    job.meta['progress'] = 100.0
    job.meta[finished_meta_key] = True
  job.save_meta()

  try:
    create_n_commit_satjob(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      storage_file=storage_file,
      stats=result["stats"],
      avg_time=result["time"]
    )
  except:
    logzero.logfile(storage_file)
    logzero.logger.warning(traceback.format_exc())
    logzero.logfile(None)

  return job

def run_all_benchmarks(algorithm_name=None, debug_level=None):
  job = rq.get_current_job()
  ix = 1
  total = len(list(os.listdir(Config.SATSMT_BENCHMARK_ROOT)))
  job.meta['finished'] = False
  for benchmark_name in os.listdir(Config.SATSMT_BENCHMARK_ROOT):
    job.meta['running_benchmark'] = f"{benchmark_name} ({ix}/{total})"
    job.meta['progress'] = 0
    job.save_meta()
    run_benchmark(
      algorithm_name,
      benchmark_name,
      debug_level,
      finished_meta_key="_fin_"
    )
    ix += 1
  job.meta['finished'] = True
  job.save_meta()

def task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level):
  return task_runner_start(
    'server.task_runner.benchmark.run_benchmark',
    algorithm_name=algorithm_name,
    benchmark_name=benchmark_name,
    debug_level=debug_level
  )

def task_runner_start_algorithm_on_all_benchmarks(algorithm_name, debug_level):
  return task_runner_start(
    'server.task_runner.benchmark.run_all_benchmarks',
    algorithm_name=algorithm_name,
    debug_level=debug_level
  )
