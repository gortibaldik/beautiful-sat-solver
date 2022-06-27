import os
import pickle
import redis
import rq
import traceback
from flask import request
from logzero import logger

from server.config import Config
from server.task_runner import get_job_log_file, has_job_finished, has_job_started, task_runner_get_benchmark_progress, task_runner_start_algorithm_on_benchmark, task_runner_stop_job

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
    if not job_dict["interrupted"] and not has_job_finished(job):
      return "<strong>No log file yet!</strong>"
    log_file = get_job_log_file(job)
    logs = ""
    with open(log_file, 'r') as l:
      for line in l:
        line = line.strip()
        logs += f"{line}</br>"
    job_dict["logs"] = logs
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
      if not saved_jobs[key]["interrupted"] and not has_job_finished(job):
        benchmark_name = key.split(',')[1]
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
    task_runner_stop_job(job)
    saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["interrupted"] = True
    return True
  logger.warning("Job cannot be stopped!")
  return False

def get_benchmark_names():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  return list(os.listdir(benchmark_root))

def get_benchmark_progress(algorithm_name, benchmark_name, saved_jobs):
  return task_runner_get_benchmark_progress(rq.job.Job.fetch(saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["job"], connection=redis.Redis.from_url('redis://')))

def start_algorithm_on_benchmark(algorithm_name, benchmark_name):
  return task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name)

def get_key(key, connection=None):
  if not connection:
    with redis.Redis.from_url('redis://') as connection:
      return pickle.loads(connection.get(key))
  return pickle.loads(connection.get(key))

def get_saved_jobs(connection=None):
  return get_key('saved_jobs', connection)

def get_algorithms_infos(connection=None):
  return get_key('algorithms_infos', connection)

def set_key(key, value, connection=None):
  svalue = pickle.dumps(value)
  if not connection:
    with redis.Redis.from_url('redis://') as connection:
      print(f"{key}: {svalue}")
      connection.set(key, svalue)
  connection.set(key, svalue)

def set_saved_jobs(value, connection=None):
  set_key('saved_jobs', value, connection)

def set_algorithms_infos(value, connection=None):
  set_key('algorithms_infos', value, connection)
