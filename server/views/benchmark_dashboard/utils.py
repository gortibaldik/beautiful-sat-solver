import os
import rq
from flask import request
from logzero import logger

from server.config import Config
from server.task_runner import (
  get_job_log_file,
  has_job_finished,
  has_job_started,
  task_runner_get_benchmark_progress,
  task_runner_get_job,
  task_runner_start_algorithm_on_benchmark,
  task_runner_stop_job
)
from server.utils.log_utils import get_log_file_content
from server.utils.redis_utils import (
  get_saved_jobs
)

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

def find_running_benchmark(algo_name, saved_jobs):
  # finds all the jobs executing algorithm algo_name and
  # checks whether they're still running
  for key in saved_jobs.keys():
    if algo_name in key:
      try:
        job = task_runner_get_job(saved_jobs[key])
      except:
        continue
      
      if ('interrupted' not in job.meta or not job.meta['interrupted'] ) and not has_job_finished(job):
        benchmark_name = key.split(',')[1]
        logger.warning(job.meta)
        return {
          "running": True,
          "benchmarkName": benchmark_name
        }
  return {
    "running": False,
    "benchmarkName": ""
  }

def get_running_status(benchmarkable_algorithms, saved_jobs):
  running_statuses = []
  for ba in benchmarkable_algorithms:
    running_statuses.append(find_running_benchmark(ba["name"], saved_jobs))
  return running_statuses

def construct_index(algorithm_name, benchmark_name):
  return f"{algorithm_name},{benchmark_name}"

def save_job(job: rq.job.Job, algorithm_name, benchmark_name, saved_jobs):
  index = construct_index(algorithm_name, benchmark_name)
  saved_jobs[index] = {
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
  logger.warning("Job cannot be stopped!")
  return False

def benchmark_name_sorting_criterion(x):
  if "uuf" in x:
    value = int(x[3:].split('-')[0]) + 10_000
  elif "uf" in x:
    value = int(x[2:].split('-')[0])
  elif "task" in x:
    value = 1
  return value

def get_benchmark_names():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  benchmark_names = list(os.listdir(benchmark_root))
  sorted_benchmark_names = sorted(benchmark_names, key=benchmark_name_sorting_criterion)
  return sorted_benchmark_names

def get_job_info(algorithm_name, benchmark_name, saved_jobs):
  index = construct_index(algorithm_name, benchmark_name)
  if index not in saved_jobs:
    raise RuntimeError(f"{index} not in saved_jobs")
  return saved_jobs[index]

def get_benchmark_progress(algorithm_name, benchmark_name):
  saved_jobs = get_saved_jobs()
  job_info = get_job_info(algorithm_name, benchmark_name, saved_jobs)
  return task_runner_get_benchmark_progress(job_info)

def start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level):
  return task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level)