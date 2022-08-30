from enum import Enum
from typing import Any, Dict

from server.task_runner import has_job_finished, task_runner_get_job
class RunningJobType(Enum):
  BENCHMARK = "benchmark"
  ALL_BENCHMARKS = "all_benchmarks"
  CUSTOM_RUN = "custom_run"

def job_is_running(job):
  return ('interrupted' not in job.meta \
          or not job.meta['interrupted'] ) \
          and not has_job_finished(job)


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
