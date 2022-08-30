import os
import rq
from flask import request
from logzero import logger

from server.config import Config
from server.get_running_job import RunningJobType, find_running_job
from server.task_runner import (
  get_job_log_file,
  has_job_finished,
  has_job_started,
  task_runner_get_all_benchmarks_progress,
  task_runner_get_benchmark_progress,
  task_runner_get_job,
  task_runner_start_algorithm_on_all_benchmarks,
  task_runner_start_algorithm_on_benchmark,
  task_runner_stop_all_run_job,
  task_runner_stop_job
)
from server.utils.log_utils import get_log_file_content
from server.utils.redis_utils import (
  get_saved_jobs
)

def get_post_algo_name():
  post_data = request.get_json()
  algorithm_name = post_data.get('algorithm')
  return algorithm_name

def get_post_data():
  post_data = request.get_json()
  algorithm_name = post_data.get('algorithm')
  benchmark_name = post_data.get('benchmark')
  return algorithm_name, benchmark_name

def get_post_debug_level():
  post_data = request.get_json()
  return post_data.get('logLevel')

def retrieve_log_file(algorithm_name, benchmark_name):
  try:
    saved_jobs = get_saved_jobs()
    job_info = get_job_info(algorithm_name, benchmark_name, saved_jobs)
  except:
    logger.warning(saved_jobs)
    raise
  if job_info["logs"] is None:
    job = task_runner_get_job(job_info)
    log_file = get_job_log_file(job)
    job_info["logs"] = "<strong>No log file yet!</strong>" if not log_file else get_log_file_content(log_file)
  return job_info["logs"]

def job_is_running(job):
  return ('interrupted' not in job.meta or not job.meta['interrupted'] ) and not has_job_finished(job)

def get_running_status(benchmarkable_algorithms, saved_jobs):
  running_statuses = []
  key, result = find_running_job(saved_jobs)
  not_running_dict = {
    "running": False,
    "all": False,
    "benchmarkName": ""
  }
  running_dict = {
    "running": True
  }
  if result is None or result not in [RunningJobType.ALL_BENCHMARKS, RunningJobType.BENCHMARK]:
    for ba in benchmarkable_algorithms:
      running_statuses.append(not_running_dict)
    return running_statuses

  if result == RunningJobType.ALL_BENCHMARKS:
    algo = key
    running_dict["all"] = True
  elif result == RunningJobType.BENCHMARK:
    algo, bench = key.split(',')
    running_dict["benchmarkName"] = bench
    running_dict["all"] = False
  
  running_dict["options"]= ";".join(algo.split(';')[1:])
  algo_stripped = algo.split(';')[0]

  for ba in benchmarkable_algorithms:
    if ba["name"] != algo_stripped:
      running_statuses.append(not_running_dict)
    else:
      running_statuses.append(running_dict)
  return running_statuses

def create_running_job_dict(
  algorithm_name,
  benchmark_name
):
  return {
    "algorithm": algorithm_name,
    "benchmark": benchmark_name
  }

def get_running_benchmark(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result not in [RunningJobType.ALL_BENCHMARKS, RunningJobType.BENCHMARK]:
    return create_running_job_dict("none", "none")
  if result == RunningJobType.ALL_BENCHMARKS:
    return create_running_job_dict(key, '__all__')
  elif result == RunningJobType.BENCHMARK:
    return create_running_job_dict(*key.split(','))
  else:
    raise RuntimeError(f"KEY: {key} should be one of ALL_BENCHMARKS, BENCHMARK types")

def construct_index(algorithm_name, benchmark_name):
  return f"{algorithm_name},{benchmark_name}"

def save_job(job: rq.job.Job, algorithm_name, benchmark_name, saved_jobs):
  index = construct_index(algorithm_name, benchmark_name)
  saved_jobs[index] = {
    "job": job.get_id(),
    "logs": None,
    "interrupted": False 
  }

def save_job_all_benchmarks(job: rq.job.Job, algorithm_name, saved_jobs):
  saved_jobs[algorithm_name] = {
    "job": job.get_id(),
    "logs": None,
    "interrupted": False
  }

def stop_job(algorithm_name, benchmark_name, saved_jobs):
  job_info = get_job_info(algorithm_name, benchmark_name, saved_jobs)
  job = task_runner_get_job(job_info)
  if has_job_started(job) and not has_job_finished(job):
    task_runner_stop_job(job, algorithm_name, benchmark_name)
    return True
  logger.warning(f"Job [{construct_index(algorithm_name, benchmark_name)}] cannot be stopped!")
  return False

def stop_job_all_run(algorithm_name, saved_jobs):
  job_info = get_all_run_job_info(algorithm_name, saved_jobs)
  job = task_runner_get_job(job_info)
  if has_job_started(job) and not has_job_finished(job):
    task_runner_stop_all_run_job(job, algorithm_name)
    return True
  logger.warning(f"Job [{algorithm_name}] cannot be stopped!")

def benchmark_name_sorting_criterion(x):
  if "uuf" in x:
    value = int(x[3:].split('-')[0]) + 30_000
  elif "uf" in x:
    value = int(x[2:].split('-')[0]) + 10_000
  elif "task" in x:
    value = 1
  elif "flat" in x:
    value = int((x[4:].split('-')[0]))
  else:
    value = x
  return value

def get_benchmark_names():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  benchmark_names = list(os.listdir(benchmark_root))
  sorted_benchmark_names = sorted(benchmark_names, key=benchmark_name_sorting_criterion)
  return sorted_benchmark_names

def get_job_info(algorithm_name, benchmark_name, saved_jobs):
  index = construct_index(algorithm_name, benchmark_name)
  if index not in saved_jobs:
    raise RuntimeError(f"{index} not in saved_jobs" + "\n" + f"saved_jobs: {saved_jobs}")
  return saved_jobs[index]

def get_all_run_job_info(algorithm_name, saved_jobs):
  if algorithm_name not in saved_jobs:
    raise RuntimeError(f"{algorithm_name} not in saved_jobs: {saved_jobs}")
  return saved_jobs[algorithm_name]

def get_benchmark_progress(algorithm_name, benchmark_name):
  saved_jobs = get_saved_jobs()
  job_info = get_job_info(algorithm_name, benchmark_name, saved_jobs)
  return task_runner_get_benchmark_progress(job_info)

def get_all_run_progress(algorithm_name):
  saved_jobs = get_saved_jobs()
  job_info = get_all_run_job_info(algorithm_name, saved_jobs)
  return task_runner_get_all_benchmarks_progress(job_info)

def start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level):
  key, result = find_running_job(get_saved_jobs())
  if result is not None:
    raise RuntimeError(f"Cannot run multiple jobs at once ! (running job key: {key})")
  return task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level)

def start_algorithm_on_all_benchmarks(algorithm_name, debug_level):
  key, result = find_running_job(get_saved_jobs())
  if result is not None:
    raise RuntimeError(f"Cannot run multiple jobs at once ! (running job key: {key})")
  return task_runner_start_algorithm_on_all_benchmarks(algorithm_name, debug_level)