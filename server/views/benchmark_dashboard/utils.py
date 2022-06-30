import os
import pickle
import redis
import rq
from flask import request
from logzero import logger

from server.config import Config
from server.task_runner import (
  get_job_log_file,
  has_job_finished,
  has_job_started,
  task_runner_get_benchmark_progress,
  task_runner_start_algorithm_on_benchmark,
  task_runner_stop_job
)
from server.utils.log_utils import get_log_file_content

def get_post_data():
  post_data = request.get_json()
  algorithm_name = post_data.get('algorithm')
  benchmark_name = post_data.get('benchmark')
  return algorithm_name, benchmark_name

def retrieve_log_file(algorithm_name, benchmark_name, saved_jobs):
  try:
    job_dict = saved_jobs[saved_job_index(algorithm_name, benchmark_name)]
  except:
    logger.warning(saved_jobs)
    raise
  if job_dict["logs"] is None:
    job = rq.job.Job.fetch(saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["job"], connection=redis.Redis.from_url('redis://'))
    log_file = get_job_log_file(job)
    job_dict["logs"] = "<strong>No log file yet!</strong>" if not log_file else get_log_file_content(log_file)
  return job_dict["logs"]

def find_running_benchmark(algo_name, saved_jobs):
  # finds all the jobs running algorithm algo_name and
  # checks whether they're still running
  for key in saved_jobs.keys():
    if algo_name in key:
      try:
        job = rq.job.Job.fetch(saved_jobs[key]["job"], connection=redis.Redis.from_url('redis://'))
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

def saved_job_index(algorithm_name, benchmark_name):
  return f"{algorithm_name},{benchmark_name}"

def save_job(job: rq.job.Job, algorithm_name, benchmark_name, saved_jobs):
  saved_jobs[saved_job_index(algorithm_name, benchmark_name)] = {
    "job": job.get_id(),
    "logs": None,
    "interrupted": False 
  }

def stop_job(algorithm_name, benchmark_name, saved_jobs):
  job = rq.job.Job.fetch(saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["job"], connection=redis.Redis.from_url('redis://'))
  if has_job_started(job) and not has_job_finished(job):
    task_runner_stop_job(job, algorithm_name, benchmark_name)
    job.meta["interrupted"] = True
    job.save_meta()
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

def get_benchmark_progress(algorithm_name, benchmark_name, saved_jobs):
  return task_runner_get_benchmark_progress(rq.job.Job.fetch(saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["job"], connection=redis.Redis.from_url('redis://')))

def start_algorithm_on_benchmark(algorithm_name, benchmark_name):
  return task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name)