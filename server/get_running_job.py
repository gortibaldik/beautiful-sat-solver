from enum import Enum
from logzero import logger
from server.task_runner import has_job_finished, has_job_started, task_runner_get_job, task_runner_stop_job
from typing import Any, Dict

class RunningJobType(Enum):
  BENCHMARK = "benchmark"
  ALL_BENCHMARKS = "all_benchmarks"
  CUSTOM_RUN = "custom_run"

def job_is_running(job):
  return ('interrupted' not in job.meta \
          or not job.meta['interrupted'] ) \
          and not has_job_finished(job)

def construct_benchmark_index(algorithm_name, benchmark_name):
  return f"{algorithm_name},{benchmark_name}"

def construct_all_run_index(algorithm_name):
  return algorithm_name

def construct_custom_run_index(algorithm_name, benchmark_name, entry_name):
  return f"{algorithm_name},{benchmark_name},{entry_name}"

def get_job_info(index, saved_jobs):
  if index not in saved_jobs:
    raise RuntimeError(f"{index} not in saved_jobs" + "\n" + f"saved_jobs: {saved_jobs}")
  return saved_jobs[index]

def stop_job(index, saved_jobs):
  job_info = get_job_info(index, saved_jobs)
  job = task_runner_get_job(job_info)
  if has_job_started(job) and not has_job_finished(job):
    task_runner_stop_job(job)
    return True
  logger.warning(f"Job [{index}] cannot be stopped!")
  return False

def is_running(saved_jobs, key):
  try:
    job = task_runner_get_job(saved_jobs[key])
  except:
    return False
  
  return job_is_running(job)

def find_running_job(saved_jobs: Dict[str, Any]):
  for key in saved_jobs.keys():
    if is_running(saved_jobs, key):
      key_parts = key.split(',')
      if len(key_parts) == 1:
        return key, RunningJobType.ALL_BENCHMARKS
      if len(key_parts) == 2:
        return key, RunningJobType.BENCHMARK
      if len(key_parts) == 3:
        return key, RunningJobType.CUSTOM_RUN
      else:
        raise RuntimeError(f"WRONG KEY in saved_jobs: key: {key} ; saved_jobs: {saved_jobs}")

  return None, None
