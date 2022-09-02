import os
import rq

from pathlib import Path
from rq.command import send_stop_job_command
from server.config import Config
from server.utils.redis_utils import get_redis_connection
from time import gmtime, strftime


def get_timestamp():
  return strftime("%Y_%m_%d_%H_%M_%S", gmtime())

def ensure_storage_file(algorithm_name, benchmark_name):
  if not algorithm_name or not benchmark_name:
    return None
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, f"{algorithm_name}_{benchmark_name}_{get_timestamp()}")
  return storage_file

def ensure_storage_file_custom_run():
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, Config.SATSOLVER_CUSTOM_RUN_FILENAME)
  return storage_file


def retrieve_algorithm(algorithms, algorithm_name):
  algorithm_name, *algorithm_parameters = algorithm_name.split(";")
  parameter_dict = {}
  for p in algorithm_parameters:
    parameter, value = p.split("=")
    if value == "true":
      value = True
    elif value == "false":
      value = False
    elif value == "None":
      value = None
    try:
      value = int(value)
    except:
      try:
        value = float(value)
      except:
        pass
    parameter_dict[parameter] = value

  for _, algo_module in algorithms.items():
    task_info = algo_module.get_info()
    if task_info["name"] == algorithm_name:
      return lambda **kwargs: algo_module.find_model(**kwargs, **parameter_dict)
  return None

def retrieve_benchmark_basedir(benchmark_name):
  all_benchmarks_basedir = Config.SATSMT_BENCHMARK_ROOT
  benchmark_name = os.path.basename(benchmark_name)
  benchmark_basedir = os.path.join(all_benchmarks_basedir, benchmark_name)

  if not os.path.isdir(benchmark_basedir):
    return None
  
  return benchmark_basedir

def retrieve_benchmark_filename(benchmark_name, entry_name):
  benchmark_basedir = retrieve_benchmark_basedir(benchmark_name)
  
  if not benchmark_basedir:
    return None

  benchmark_filename = os.path.join(benchmark_basedir, entry_name)
  if not os.path.isfile(benchmark_filename):
    return None
  return benchmark_filename

def retrieve_benchmark_filenames(benchmark_name):
  benchmark_basedir = retrieve_benchmark_basedir(benchmark_name)
  
  if not benchmark_basedir:
    return None
  
  benchmark_filenames = []
  for f in os.listdir(benchmark_basedir):
    benchmark_filenames.append(os.path.join(benchmark_basedir, f))
  
  return benchmark_filenames

def task_runner_get_progress(job_info, return_model=False):
  job = task_runner_get_job(job_info)
  job.refresh()
  value, model = None, None
  if 'interrupted' in job.meta and job.meta['interrupted']:
    value = 100
  elif 'finished' in job.meta and job.meta['finished']:
    value = 100
  elif not 'progress' in job.meta:
    value = 0
  else:
    value = job.meta['progress']

  if return_model:
    model = job.meta.get("model", None)
    return value, model
  else:
    return value

def task_runner_get_all_benchmarks_progress(job_info):
  job = task_runner_get_job(job_info)
  job.refresh()
  if 'interrupted' in job.meta and job.meta['interrupted']:
    return 100, None, True
  if 'finished' in job.meta and job.meta['finished']:
    return 100, None, True
  if not 'progress' in job.meta or not 'running_benchmark' in job.meta or not 'finished' in job.meta:
    return 0, None, False
  return job.meta['progress'], job.meta['running_benchmark'], job.meta['finished']

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

def get_custom_run_log_file():
  log_filename = os.path.join(
    Config.SATSMT_RESULT_LOGS,
    Config.SATSOLVER_CUSTOM_RUN_FILENAME
  )

  if os.path.isfile(log_filename):
    return log_filename
  else:
    return None

def task_runner_stop_job(job:rq.job.Job):
  job.refresh()
  send_stop_job_command(get_redis_connection(), job.get_id())
  job.meta["interrupted"] = True
  job.save_meta()

def task_runner_get_job(job_info):
  return rq.job.Job.fetch(job_info["job"], connection=get_redis_connection())

def task_runner_start(method_name, **kwargs):
  queue = rq.Queue(
    Config.REDIS_WORKER_QUEUE_NAME,
    connection=get_redis_connection(),
    default_timeout=3600
  )
  job = queue.enqueue(method_name, kwargs=kwargs)
  return job
