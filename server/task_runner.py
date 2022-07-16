import traceback
import logzero
import os
import rq
import server.getters

from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from rq.command import send_stop_job_command
from satsolver.utils.check import check_assignment
from server.database import SessionLocal
from server.config import Config
from server.models.job import SATJob
from server.utils.redis_utils import get_redis_connection
from time import gmtime, strftime


def get_timestamp():
  return strftime("%Y_%m_%d_%H_%M_%S", gmtime())

def ensure_storage_file(algorithm_name, benchmark_name):
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, f"{algorithm_name}_{benchmark_name}_{get_timestamp()}")
  return storage_file

def create_sat_job(
  *,
  algorithm_name,
  benchmark_name,
  log_file,
  avg_time=-1,
  avg_derivs=-1,
  avg_unit_props=-1):
  sat_job = SATJob(
    unit_prop_vals  = avg_unit_props,
    decision_vars   = avg_derivs,
    time            = avg_time,
    algorithm       = algorithm_name,
    benchmark       = benchmark_name,
    log_file        = log_file
  )
  return sat_job

def create_n_commit_satjob(
  *,
  algorithm_name,
  benchmark_name,
  storage_file,
  avg_time=0,
  avg_derivs=0,
  avg_unit_props=0
):
  with SessionLocal() as db:
    sat_job = create_sat_job(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      log_file=storage_file,
      avg_time=avg_time,
      avg_derivs=avg_derivs,
      avg_unit_props=avg_unit_props
    )
    db.add(sat_job)
    db.commit()

def retrieve_algorithm(algorithms, algorithm_name):
  for _, algo_module in algorithms.items():
    task_info = algo_module.get_info()
    if task_info["name"] == algorithm_name:
      return algo_module
  return None

def retrieve_benchmark_filenames(benchmark_name):
  all_benchmarks_basedir = Config.SATSMT_BENCHMARK_ROOT
  benchmark_name = os.path.basename(benchmark_name)
  benchmark_basedir = os.path.join(all_benchmarks_basedir, benchmark_name)
  
  if not os.path.isdir(benchmark_basedir):
    return None
  
  benchmark_filenames = []
  for f in os.listdir(benchmark_basedir):
    benchmark_filenames.append(os.path.join(benchmark_basedir, f))
  
  return benchmark_filenames

def init_cumulative_stats():
  return {
    "ndecs": 0,
    "nunit": 0,
    "time": 0,
    "total": 0,
  }

def update_cumulative_stats(
  *,
  cumulative_stats,
  result
):
  cumulative_stats["total"] += 1
  cumulative_stats["ndecs"] += result["number_of_decisions"]
  cumulative_stats["nunit"] += result["number_of_unit_props"]
  cumulative_stats["time"] += result["time"]

def avg_cumulative_stats(cumulative_stats):
  cumulative_stats["ndecs"] /= cumulative_stats["total"]
  cumulative_stats["nunit"] /= cumulative_stats["total"]
  cumulative_stats["time"] /= cumulative_stats["total"]

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
    debug, info, warning = log_level_per_debug_level(debug_level)

    for i, filename in enumerate(benchmark_filenames):
      job.meta['progress'] = i * 100 / total_number_of_benchmarks
      job.save_meta()
      result = algo_module.find_model(
        input_file=filename,
        debug=debug,
        warning=warning,
        nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
      )
      check_assignment(
        input_file=filename,
        assignment_source=result["model"],
        debug=debug,
        warning=warning,
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
    logzero.logger.info(cumulative_stats)
  except:
    if filename is not None:
      logzero.logger.warning(f"Filename with error: {filename}")
    logzero.logger.warning(traceback.format_exc())
    return None
  
  return cumulative_stats

def run_benchmark(algorithm_name, benchmark_name, debug_level):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, benchmark_name)
  logzero.logger.info(f"Selected storage file: {storage_file}")
  job.meta['finished'] = False
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
    job.meta['finished'] = True
  job.save_meta()

  try:
    create_n_commit_satjob(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      storage_file=storage_file,
      avg_derivs=result["ndecs"],
      avg_unit_props=result["nunit"],
      avg_time=result["time"]
    )
  except:
    logzero.logfile(storage_file)
    logzero.logger.warning(traceback.format_exc())
    logzero.logfile(None)

  return job

def task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level):
  queue = rq.Queue(
    Config.REDIS_WORKER_QUEUE_NAME,
    connection=get_redis_connection(),
    default_timeout=3600
   )
  job = queue.enqueue('server.task_runner.run_benchmark', algorithm_name, benchmark_name, debug_level)
  return job

def task_runner_get_benchmark_progress(job_info):
  job = task_runner_get_job(job_info)
  job.refresh()
  if 'interrupted' in job.meta and job.meta['interrupted']:
    return 100
  if 'finished' in job.meta and job.meta['finished']:
    return 100
  if not 'progress' in job.meta:
    raise RuntimeError("Caught no progress exception!")
  return job.meta['progress']

def has_job_finished(job):
  try:
    job.refresh()
    return job.meta["finished"]
  except:
    return False

def has_job_started(job: rq.job.Job):
  try:
    job.refresh()
    return "finished" in job.meta
  except Exception as e:
    return False

def get_job_log_file(job):
  job.refresh()
  if 'storage_file' not in job.meta:
    return None
  return job.meta["storage_file"]

def task_runner_stop_job(job:rq.job.Job, algorithm_name, benchmark_name):
  job.refresh()
  storage_file = job.meta["storage_file"]
  send_stop_job_command(get_redis_connection(), job.get_id())
  job.meta["interrupted"] = True
  job.save_meta()
  try:
    create_n_commit_satjob(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      storage_file=storage_file
    )
  except:
    logzero.logfile(storage_file)
    logzero.logger.warning("Caught exception when saving results to the database")
    logzero.logfile(None)

def task_runner_get_job(job_info):
  return rq.job.Job.fetch(job_info["job"], connection=get_redis_connection())
