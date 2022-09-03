from flask import Blueprint, jsonify
from logzero import logger
from server.config import Config
from server.utils.exception_utils import on_exception_result_failure, on_success_result_success
from server.utils.redis_utils import (
  get_algorithms_infos,
  get_saved_jobs,
  set_saved_jobs,
  get_redis_connection,
)
from server.views.benchmark_dashboard.utils import (
  get_all_run_progress,
  get_benchmark_names,
  get_benchmark_progress,
  get_post_algo_name,
  get_post_data,
  get_post_debug_level,
  get_running_benchmark,
  get_running_status,
  retrieve_log_file,
  save_job,
  save_job_all_benchmarks,
  start_algorithm_on_all_benchmarks,
  start_algorithm_on_benchmark,
  stop_job_benchmark,
  stop_job_all_run
)

benchmark_page = Blueprint('benchmark_page', __name__)

@benchmark_page.route('/', methods=['GET'])
@on_exception_result_failure
def algorithm_index():
  with get_redis_connection() as connection:
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

@benchmark_page.route('/start', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def start_algorithm():
  saved_jobs = get_saved_jobs()
  algorithm_name, benchmark_name = get_post_data()
  debug_level = get_post_debug_level()
  job = start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level)
  save_job(job, algorithm_name, benchmark_name, saved_jobs)
  set_saved_jobs(saved_jobs)

@benchmark_page.route('/stop', methods=['POST'])
@on_exception_result_failure
def stop_algorithm():
  saved_jobs = get_saved_jobs()
  algorithm_name, benchmark_name = get_post_data()
  if stop_job_benchmark(algorithm_name, benchmark_name, saved_jobs):
    logger.info(saved_jobs)
    set_saved_jobs(saved_jobs)
    return jsonify({'result': 'success'})
  return jsonify({'result': 'failure'})

@benchmark_page.route('/progress', methods=['POST'])
@on_exception_result_failure
def get_progress():
  algorithm_name, benchmark_name = get_post_data()
  progress = get_benchmark_progress(algorithm_name, benchmark_name)
  return jsonify({'result': progress})

@benchmark_page.route('/start_all', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def start_all_benchmarks():
  saved_jobs = get_saved_jobs()
  algorithm_name = get_post_algo_name()
  debug_level = get_post_debug_level()
  job = start_algorithm_on_all_benchmarks(algorithm_name, debug_level)
  save_job_all_benchmarks(job, algorithm_name, saved_jobs)
  set_saved_jobs(saved_jobs)

@benchmark_page.route('/progress_all', methods=['POST'])
@on_exception_result_failure
def get_progress_all():
  algorithm_name = get_post_algo_name()
  progress, benchmark_name, finished = get_all_run_progress(algorithm_name)
  return jsonify({
    'result':         progress,
    'benchmark_name': benchmark_name,
    'finished':       finished
  })

@benchmark_page.route('stop_all', methods=['POST'])
@on_exception_result_failure
def stop_all_benchmarks():
  algorithm_name = get_post_algo_name()
  saved_jobs = get_saved_jobs()
  if stop_job_all_run(algorithm_name, saved_jobs):
    set_saved_jobs(saved_jobs)
    return jsonify({'result': 'success'})
  return jsonify({'result': 'failure'})

@benchmark_page.route('/result', methods=['POST'])
@on_exception_result_failure
def get_result():
  algorithm_name, benchmark_name = get_post_data()
  log_file = retrieve_log_file(algorithm_name, benchmark_name)
  return jsonify({ "result" : log_file })

@benchmark_page.route('/get_running_benchmark', methods=['GET'])
@on_exception_result_failure
def running_benchmark():
  saved_jobs = get_saved_jobs()
  return jsonify({ 'result': get_running_benchmark(saved_jobs)})
