from flask import Blueprint, jsonify
from server.utils.exception_utils import on_exception_result_failure, on_success_result_success
from server.utils.redis_utils import (
  get_algorithms_infos,
  get_saved_jobs,
  get_redis_connection,
  set_saved_jobs,
)
from server.views.custom_run.utils import (
  get_benchmarks,
  get_post_data,
  get_post_debug_level,
  get_running_job,
  is_custom_run_finished,
  retrieve_log_file_content,
  save_job,
  start_algorithm_on_custom_run,
  stop_algorithm_on_custom_run,
)

custom_run_page = Blueprint('custom_run_page', __name__)

@custom_run_page.route('/', methods=['GET'])
@on_exception_result_failure
def custom_run_index():
  with get_redis_connection() as connection:
    algorithms_infos = get_algorithms_infos(connection)
    saved_jobs = get_saved_jobs(connection)
  # logger.info(algorithms_infos)
  # logger.info(saved_jobs)
  benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
  return jsonify({
    "result": "success",
    "benchmarks": get_benchmarks(),
    "algorithms": benchmarkable_algorithms,
    "running_job": get_running_job(saved_jobs)
  })

@custom_run_page.route('/get_running_custom_run', methods=['GET'])
@on_exception_result_failure
def get_running_custom_run():
  saved_jobs = get_saved_jobs()
  return jsonify({
    'result': 'success',
    'running_job': get_running_job(saved_jobs)
  })

@custom_run_page.route('/start', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def start_custom_run():
  saved_jobs = get_saved_jobs()
  algorithm_name, benchmark_name, entry_name = get_post_data()
  debug_level = get_post_debug_level()
  job = start_algorithm_on_custom_run(
    algorithm_name,
    benchmark_name,
    entry_name,
    debug_level
  )
  save_job(
    job,
    algorithm_name,
    benchmark_name,
    entry_name,
    saved_jobs
  )
  set_saved_jobs(saved_jobs)

@custom_run_page.route('/stop', methods=['POST'])
@on_exception_result_failure
def stop_custom_run():
  saved_jobs = get_saved_jobs()
  algorithm_name, benchmark_name, entry_name = get_post_data()
  if stop_algorithm_on_custom_run(
      algorithm_name,
      benchmark_name,
      entry_name,
      saved_jobs
  ):
    return jsonify({'result': 'success'})
  return jsonify({'result': 'failure'})

@custom_run_page.route('/get_logs', methods=['GET'])
@on_exception_result_failure
def get_custom_run_logs():
  log_file_content = retrieve_log_file_content()
  return jsonify({ 'result': log_file_content})

@custom_run_page.route('/is_finished', methods=['POST'])
@on_exception_result_failure
def is_finished():
  algorithm_name, benchmark_name, entry_name = get_post_data()
  is_finished = is_custom_run_finished(
    algorithm_name,
    benchmark_name,
    entry_name
  )
  return jsonify({'result': 'yes' if is_finished else 'no'})
