import os

from flask import request
from logzero import logger
from server.config import Config
from server.task_runner import get_custom_run_log_file, task_runner_get_progress, task_runner_start_algorithm_on_custom_run
from server.utils.log_utils import get_log_file_content
from server.get_running_job import RunningJobType, construct_custom_run_index, find_running_job, get_job_info, stop_job
from server.utils.redis_utils import get_saved_jobs
from server.views.benchmark_dashboard.utils import benchmark_name_sorting_criterion

def get_benchmarks():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  benchmark_names = list(os.listdir(benchmark_root))
  benchmarks = []
  for b in sorted(benchmark_names, key=benchmark_name_sorting_criterion):
    benchmark_dir = os.path.join(benchmark_root, b)
    benchmark_entries = list(os.listdir(benchmark_dir))
    
    benchmark_entries_sorted = sorted(benchmark_entries, key=benchmark_name_sorting_criterion)
    
    entry = {
      "name": b,
      "inputs": benchmark_entries_sorted
    }

    benchmarks.append(entry)
  return benchmarks

def get_benchmark_post_data():
  post_data = request.get_json()
  benchmark_name = post_data.get('benchmark')
  entry_name     = post_data.get('entry')
  return benchmark_name, entry_name

def get_post_data():
  post_data = request.get_json()
  algorithm_name  = post_data.get('algorithm')
  benchmark_name, entry_name = get_benchmark_post_data()
  return algorithm_name, benchmark_name, entry_name

def get_post_debug_level():
  post_data = request.get_json()
  return post_data.get('logLevel')

def retrieve_log_file_content():
  log_filename = get_custom_run_log_file()
  if log_filename is None:
    return "<code>No log file yet</code>"
  
  log_file_content = get_log_file_content(log_filename)
  return log_file_content

def is_custom_run_finished(
  algorithm_name,
  benchmark_name,
  entry_name,
  saved_jobs=None
):
  if saved_jobs is None:
    saved_jobs = get_saved_jobs()
  index = construct_custom_run_index(
    algorithm_name,
    benchmark_name,
    entry_name
  )
  job_info = get_job_info(index, saved_jobs)
  return task_runner_get_progress(job_info) == 100
  

def start_algorithm_on_custom_run(
  algorithm_name,
  benchmark_name,
  entry_name,
  debug_level
):
  key, result = find_running_job(get_saved_jobs())
  if result is not None:
    raise RuntimeError(f"Cannot run multiple jobs at once ! (running job key: {key})")
  return task_runner_start_algorithm_on_custom_run(
    algorithm_name,
    benchmark_name,
    entry_name,
    debug_level
  )

def stop_algorithm_on_custom_run(
  algorithm_name,
  benchmark_name,
  entry_name,
  saved_jobs
):
  index = construct_custom_run_index(
    algorithm_name,
    benchmark_name,
    entry_name
  )
  stop_job(index, saved_jobs)
  return False


def save_job(
  job,
  algorithm_name,
  benchmark_name,
  entry_name,
  saved_jobs
):
  index = construct_custom_run_index(
    algorithm_name,
    benchmark_name,
    entry_name
  )
  saved_jobs[index] = {
    "job": job.get_id(),
    "logs": None,
  }

def create_running_job_dict(
  algorithm_name,
  benchmark_name,
  entry_name
):
  return {
    "algorithm": algorithm_name,
    "benchmark": benchmark_name,
    "entry": entry_name
  }

def get_running_custom_run(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result != RunningJobType.CUSTOM_RUN:
    return create_running_job_dict("none", "none", "none")

  algo, bench, entry = key.split(',')
  return create_running_job_dict(algo, bench, entry)

def get_benchmark_entry_content(benchmark_name, entry_name):
  benchmark_dir = os.path.join(Config.SATSMT_BENCHMARK_ROOT, benchmark_name)
  if ".." in benchmark_name or not os.path.isdir(benchmark_dir):
    raise RuntimeError(f"{benchmark_name} is not a valid benchmark name !")
  
  entry_filename = os.path.join(benchmark_dir, entry_name)
  if ".." in entry_filename or not os.path.isfile(entry_filename):
    raise RuntimeError(f"{entry_name} is not a valid benchmark entry name ({benchmark_name})!")
  
  content = ""
  with open(entry_filename, 'r') as f:
    for line in f:
      line = line.strip()
      content += f"{line}</br>"
  return content
