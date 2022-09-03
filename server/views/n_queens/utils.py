from flask import request
from satsolver.utils.general_setup import TypeOfOption, create_option
from server.get_running_job import RunningJobType, construct_nqueens_index, find_running_job, get_job_info, stop_job
from server.task_runner.nqueens import task_runner_start_algorithm_on_nqueens
from server.task_runner.utils import task_runner_get_progress
from server.utils.redis_utils import get_saved_jobs
from server.views.benchmark_dashboard.utils import retrieve_log_file_from_index

def get_running_nqueens(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result != RunningJobType.NQUEENS:
    return { "algorithm": "none" }
  else:
    algo, problem, descr1, descr2 = key.split(",")
    run_as_benchmark = descr1 == "benchmark"
    N = 8
    timeout = 30
    if not run_as_benchmark:
      N = int(descr1)
    else:
      timeout = int(descr2)
    return {
      "algorithm": algo,
      "run_as_benchmark": run_as_benchmark,
      "N":         N,
      "timeout":   timeout
    }

def get_nqueens_parameters():
  return [
    create_option(
      name="N",
      hint="Number of queens to place, size of the board",
      type=TypeOfOption.VALUE,
      default=8
    ),
    create_option(
      name="run_as_benchmark",
      hint="If checked, the selected algorithm runs for increasing N (1, 2, 3...) " +\
        "and stops when timeout is reached (e.g. if the algorithm runs more than T " +\
        " seconds for N=n then that run is interrupted and the suite is ended)",
      type=TypeOfOption.CHECKBOX,
      default=False
    ),
    create_option(
      name="timeout",
      hint="How many SECONDS the algorithm should run before abort",
      type=TypeOfOption.VALUE,
      default=30
    )
  ]

def get_post_N():
  post_data = request.get_json()
  N = post_data.get('N')
  return N

def get_post_data():
  post_data = request.get_json()
  algorithm        = post_data.get('algorithm')
  n                = post_data.get('N')
  run_as_benchmark = post_data.get('run_as_benchmark')
  timeout          = post_data.get('timeout')
  return algorithm, n, run_as_benchmark, timeout

def save_job(
  job,
  algorithm_name,
  n,
  run_as_benchmark,
  timeout,
  saved_jobs
):
  index = construct_nqueens_index(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout
  )
  saved_jobs[index] = {
    "job": job.get_id(),
    "logs": None
  }

def start_algorithm_on_nqueens(
  algorithm_name,
  n,
  run_as_benchmark,
  timeout,
  debug_level
):
  key, result = find_running_job(get_saved_jobs())
  if result is not None:
    raise RuntimeError(f"Cannot run multiple jobs at once ! (running job key: {key})")
  return task_runner_start_algorithm_on_nqueens(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout,
    debug_level
  )

def retrieve_log_file(
  algorithm_name,
  n,
  run_as_benchmark,
  timeout
):
  index = construct_nqueens_index(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout
  )
  return retrieve_log_file_from_index(index)

def stop_job_nqueens(
  algorithm_name,
  n,
  run_as_benchmark,
  timeout,
  saved_jobs
):
  index = construct_nqueens_index(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout
  )
  return stop_job(index, saved_jobs)

def is_nqueens_finished(
  algorithm_name,
  n,
  run_as_benchmark,
  timeout,
  saved_jobs=None
):
  if saved_jobs is None:
    saved_jobs = get_saved_jobs()
  index = construct_nqueens_index(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout
  )
  job_info = get_job_info(index, saved_jobs)
  progress, model = task_runner_get_progress(job_info, return_model=True)
  return progress == 100, model
