from flask import request
from logzero import logger
from server.get_running_job import find_running_job, get_job_info, stop_job
from server.task_runner.utils import task_runner_get_progress
from server.utils.redis_utils import get_saved_jobs
from server.views.benchmark_dashboard.utils import retrieve_log_file_from_index


def start_algorithm_on_problem(
  task_runner_start_problem,
  **kwargs
):
  key, result = find_running_job(get_saved_jobs())
  if result is not None:
    raise RuntimeError(f"Cannot run multiple jobs at once ! (running job key: {key})")
  return task_runner_start_problem(**kwargs)

def save_job(
  job,
  saved_jobs,
  construct_index,
  **kwargs
):
  index = construct_index(**kwargs)
  saved_jobs[index] = {
    "job": job.get_id(),
    "logs": None
  }

def get_post_data(post_data_array):
  post_data_dict = {}
  post_data = request.get_json()
  for key in post_data_array:
    post_data_dict[key] = post_data.get(key)
  logger.warning(post_data_dict)
  return post_data_dict

def retrieve_log_file(construct_index, **kwargs):
  index = construct_index(**kwargs)
  return retrieve_log_file_from_index(index)

def stop_job_on_problem(
  construct_index,
  saved_jobs,
  **kwargs
):
  index = construct_index(**kwargs)
  return stop_job(index, saved_jobs)

def is_problem_finished(
  construct_index,
  **kwargs
):
  saved_jobs = get_saved_jobs()
  index = construct_index(**kwargs)
  job_info = get_job_info(index, saved_jobs)
  progress, model = task_runner_get_progress(job_info, return_model=True)
  return progress == 100, model
