import os
import rq
import time
from contextlib import redirect_stdout
from pathlib import Path
from redis import Redis
from rq.command import send_stop_job_command
from server.config import Config
from time import gmtime, strftime

def get_timestamp():
  return strftime("%Y_%m_%d_%H_%M_%S", gmtime())

def ensure_storage_file(algorithm_name, benchmark_name):
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, f"{algorithm_name}_{benchmark_name}_{get_timestamp()}")
  return storage_file

def run_benchmark(algorithm_name, benchmark_name):
  job = rq.get_current_job()
  seconds = Config.DUMMY_RUNTIME
  storage_file = ensure_storage_file(algorithm_name, benchmark_name)
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      for i in range(seconds):
        job.meta['progress'] = i * 100 / seconds
        job.save_meta()
        print(f"{i}. second - {algorithm_name}")
        time.sleep(1)
        f.flush()
  job.meta['progress'] = 100.0
  job.meta['finished'] = True
  job.save_meta()
  return job

def task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name):
  queue = rq.Queue(os.getenv('REDIS_QUEUE_NAME'), connection=Redis.from_url('redis://'))
  job = queue.enqueue('server.task_runner.run_benchmark', algorithm_name, benchmark_name)
  return job

def task_runner_get_benchmark_progress(job):
  job.refresh()
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
  return job.meta["storage_file"]

def task_runner_stop_job(job:rq.job.Job):
  send_stop_job_command(Redis.from_url('redis://'), job.get_id())