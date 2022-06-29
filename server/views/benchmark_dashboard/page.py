import redis
import traceback

from flask import Blueprint, jsonify
from logzero import logger

from server.config import Config
from server.utils.redis_utils import (
  get_algorithms_infos,
  get_saved_jobs,
  set_saved_jobs
)
from server.views.benchmark_dashboard.utils import (
  get_benchmark_names,
  get_benchmark_progress,
  get_post_data,
  get_running_status,
  retrieve_log_file,
  save_job,
  start_algorithm_on_benchmark,
  stop_job
)

benchmark_page = Blueprint('benchmark_page', __name__)

@benchmark_page.route('/', methods=['GET'])
def algorithm_index():
  try:
    with redis.Redis.from_url('redis://') as connection:
      algorithms_infos = get_algorithms_infos(connection)
      saved_jobs = get_saved_jobs(connection)
    # logger.info(algorithms_infos)
    # logger.info(saved_jobs)
    benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
    benchmarked_result_availability = Config.BENCHMARKED_RESULTS_AVAILABILITY
    return jsonify({
      "result": "success",
      "benchmarks": get_benchmark_names(),
      "benchmarkable_algorithms_running_status": get_running_status(benchmarkable_algorithms, saved_jobs),
      "benchmarkable_algorithms": benchmarkable_algorithms,
      "benchmarked_result_availability": benchmarked_result_availability - 5000
    })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})

@benchmark_page.route('/start', methods=['POST'])
def start_algorithm():
  try:
    saved_jobs = get_saved_jobs()
    algorithm_name, benchmark_name = get_post_data()
    job = start_algorithm_on_benchmark(algorithm_name, benchmark_name)
    save_job(job, algorithm_name, benchmark_name, saved_jobs)
    set_saved_jobs(saved_jobs)
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})
  return jsonify({ 'result': 'success' })

@benchmark_page.route('/stop', methods=['POST'])
def stop_algorithm():
  try:
    saved_jobs = get_saved_jobs()
    algorithm_name, benchmark_name = get_post_data()
    if stop_job(algorithm_name, benchmark_name, saved_jobs):
      set_saved_jobs(saved_jobs)
      return jsonify({'result': 'success'})
  except:
    logger.warning(traceback.format_exc())
  return jsonify({'result': 'failure'})

@benchmark_page.route('/progress', methods=['POST'])
def get_progress():
  try:
    algorithm_name, benchmark_name = get_post_data()
    saved_jobs = get_saved_jobs()
    progress = get_benchmark_progress(algorithm_name, benchmark_name, saved_jobs)
  except:
    logger.warning(traceback.format_exc())
    return jsonify({'result': 'failure'})
  return jsonify({'result': progress})

@benchmark_page.route('/result', methods=['POST'])
def get_result():
  try:
    algorithm_name, benchmark_name = get_post_data()
    saved_jobs = get_saved_jobs()
    return jsonify({ "result" : retrieve_log_file(algorithm_name, benchmark_name, saved_jobs) })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})