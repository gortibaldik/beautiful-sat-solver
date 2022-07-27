import traceback

from flask import Blueprint, jsonify
from logzero import logger

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
  is_custom_run_finished,
  retrieve_log_file_content,
  save_job,
  start_algorithm_on_custom_run,
)

custom_run_page = Blueprint('custom_run_page', __name__)

@custom_run_page.route('/', methods=['GET'])
def custom_run_index():
  try:
    with get_redis_connection() as connection:
      algorithms_infos = get_algorithms_infos(connection)
    # logger.info(algorithms_infos)
    # logger.info(saved_jobs)
    benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
    return jsonify({
      "result": "success",
      "benchmarks": get_benchmarks(),
      "algorithms": benchmarkable_algorithms,
    })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})

@custom_run_page.route('/start', methods=['POST'])
def start_custom_run():
  try:
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
  except:
    logger.warning(traceback.format_exc())
    return jsonify({'result': 'failure'})
  return jsonify({'result': 'success'})

@custom_run_page.route('/get_logs', methods=['GET'])
def get_custom_run_logs():
  try:
    log_file_content = retrieve_log_file_content()
    return jsonify({ 'result': log_file_content})
  except:
    logger.warning(traceback.format_exc())
    return jsonify({'result': 'failure'})

@custom_run_page.route('/is_finished', methods=['POST'])
def is_finished():
  try:
    algorithm_name, benchmark_name, entry_name = get_post_data()
    is_finished = is_custom_run_finished(
      algorithm_name,
      benchmark_name,
      entry_name
    )
    return jsonify({'result': 'yes' if is_finished else 'no'})
  except:
    logger.warning(traceback.format_exc())
    return jsonify({'result': 'failure'})
