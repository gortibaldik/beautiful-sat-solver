import traceback
import logzero
import os
import random
import rq
import time

from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from redis import Redis
from rq.command import send_stop_job_command
from server.database import SessionLocal
from server.config import Config
from server.models.job import SATJob
from server.utils.redis_utils import get_algorithms_infos
from time import gmtime, strftime


def get_timestamp():
  return strftime("%Y_%m_%d_%H_%M_%S", gmtime())

def ensure_storage_file(algorithm_name, benchmark_name):
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, f"{algorithm_name}_{benchmark_name}_{get_timestamp()}")
  return storage_file

def create_sat_job(algorithm_name, benchmark_name, log_file):
  max_time = 250
  max_derivs = 30
  max_unit_props = 200
  sat_job = SATJob(
    unit_prop_vals  = random.random() * max_unit_props,
    decision_vars   = random.random() * max_derivs,
    time            = random.random() * max_time,
    algorithm       = algorithm_name,
    benchmark       = benchmark_name,
    log_file        = log_file
  )
  return sat_job

def create_n_commit_satjob(algorithm_name, benchmark_name, storage_file):
  with SessionLocal() as db:
    sat_job = create_sat_job(algorithm_name, benchmark_name, storage_file)
    db.add(sat_job)
    db.commit()

def benchmark(file, algorithm_name, benchmark_name):
  try:
    seconds = Config.DUMMY_RUNTIME
    job = rq.get_current_job()
    job.meta["progress"] = 0
    job.save_meta()
    algorithms_infos = get_algorithms_infos()
    logzero.logger.info(algorithms_infos)
    for i in range(seconds):
      job.meta['progress'] = i * 100 / seconds
      job.save_meta()
      logzero.logger.info(f"This should be written to the same file!")
      time.sleep(1)
      file.flush()
  except:
    logzero.logger.warning(traceback.format_exc())
    return False
  return True

def run_benchmark(algorithm_name, benchmark_name):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, benchmark_name)
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        result = benchmark(f, algorithm_name, benchmark_name)
        logzero.logfile(None)
  create_n_commit_satjob(algorithm_name, benchmark_name, storage_file)
  if not result:
    job.meta['interrupted'] = True
  else:
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
  if 'interrupted' in job.meta and job.meta['interrupted']:
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
  try:
    job.refresh()
    storage_file = job.meta["storage_file"]
  except:
    storage_file = "ERROR"
  send_stop_job_command(Redis.from_url('redis://'), job.get_id())
  create_n_commit_satjob(algorithm_name, benchmark_name, storage_file)