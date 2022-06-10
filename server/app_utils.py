import os
from flask import request
from logzero import logger

from server.task_runner import get_job_log_file, has_job_finished, has_job_started, task_runner_stop_job

def get_post_data():
  post_data = request.get_json()
  logger.info(f"received: {post_data}")
  algorithm_name = post_data.get('algorithm')
  benchmark_name = post_data.get('benchmark')
  return algorithm_name, benchmark_name

def get_environ(name):
  return os.getenv(name)

def retrieve_log_file(job_dict):
  if job_dict["logs"] is None:
    job = job_dict["job"]
    if not has_job_finished(job):
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
  for key in saved_jobs.keys():
    if algo_name in key:
      job = saved_jobs[key]["job"]
      if not has_job_finished(job):
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

def save_job(job, algorithm_name, benchmark_name, saved_jobs):
  saved_jobs[saved_job_index(algorithm_name, benchmark_name)] = {
    "job": job,
    "logs": None 
  }

def stop_job(algorithm_name, benchmark_name, saved_jobs):
  job = saved_jobs[saved_job_index(algorithm_name, benchmark_name)]["job"]
  if has_job_started(job) and not has_job_finished(job):
    task_runner_stop_job(job)
    saved_jobs.pop(saved_job_index(algorithm_name, benchmark_name))
    return True
  logger.warning("Job cannot be stopped!")
  return False

def get_benchmark_names():
  return [
    'firstBenchmark',
    'secondBenchmark',
    '3Benchmark',
    '4Benchmark',
    '5Benchmark',
    '6Benchmark',
    '7Benchmark',
    '8Benchmark',
    '9Benchmark',
    '10Benchmark',
  ]