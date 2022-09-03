from flask import jsonify
from server.utils.redis_utils import get_algorithms_infos, get_redis_connection, get_saved_jobs, set_saved_jobs
from server.views.custom_run.utils import get_benchmark_entry_content, get_post_debug_level
from server.views.problem_prototype.utils import get_post_data, is_problem_finished, retrieve_log_file, save_job, start_algorithm_on_problem, stop_job_on_problem


def index(get_running_job, get_parameters):
  with get_redis_connection() as connection:
    algorithms_infos = get_algorithms_infos(connection)
    saved_jobs = get_saved_jobs(connection)
  benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
  return jsonify({
    "result": "success",
    "algorithms": benchmarkable_algorithms,
    "running_job": get_running_job(saved_jobs),
    "problem_parameters": get_parameters()
  })

def start(
  post_data_array,
  task_runner_start,
  construct_index
):
  saved_jobs = get_saved_jobs()
  kwargs = get_post_data(post_data_array)
  debug_level = get_post_debug_level()
  job = start_algorithm_on_problem(task_runner_start, debug_level=debug_level, **kwargs)
  save_job(job, saved_jobs, construct_index, **kwargs)
  set_saved_jobs(saved_jobs)

def get_logs(
  post_data_array,
  construct_index
):
  kwargs = get_post_data(post_data_array)
  log_file_content = retrieve_log_file(construct_index, **kwargs)
  return jsonify({ 'result': log_file_content})

def stop(
  post_data_array,
  construct_index
):
  saved_jobs = get_saved_jobs()
  kwargs = get_post_data(post_data_array)
  if stop_job_on_problem(construct_index, saved_jobs, **kwargs):
    set_saved_jobs(saved_jobs)
    return jsonify({'result': 'success'})
  return jsonify({'result': 'failure'})

def get_progress(
  post_data_array,
  construct_index,
  should_return_model
):
  kwargs = get_post_data(post_data_array)
  is_finished, model = is_problem_finished(construct_index, **kwargs)
  if is_finished:
    return jsonify(
      result="yes",
      model=model if not should_return_model(**kwargs) else []
    )
  else:
    return jsonify(result="no")

def dimacs(
  post_data_array,
  generate_dimacs,
  problem_name,
  get_entry_name
):
  kwargs = get_post_data(post_data_array)
  dimacs_file = generate_dimacs(generate_new=False, **kwargs)
  if dimacs_file is None:
    return jsonify(result="failure")
  return jsonify(
    result="success",
    content=get_benchmark_entry_content(problem_name, get_entry_name(**kwargs))
  )
