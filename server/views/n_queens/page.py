from flask import Blueprint, jsonify
from satsolver.task6 import NQUEENS_PROBLEM_NAME, generate_nqueens_dimacs
from server.utils.exception_utils import (
  on_exception_result_failure,
  on_success_result_success,
)
from server.utils.redis_utils import (
  get_algorithms_infos,
  get_redis_connection,
  get_saved_jobs,
  set_saved_jobs,
)
from server.views.custom_run.utils import (
  get_benchmark_entry_content,
  get_post_debug_level
)
from server.views.n_queens.utils import (
  get_nqueens_parameters,
  get_post_N,
  get_post_data,
  get_running_nqueens,
  is_nqueens_finished,
  retrieve_log_file,
  save_job,
  start_algorithm_on_nqueens,
  stop_job_nqueens,
)

n_queens_page = Blueprint('n_queens_page', __name__)

@n_queens_page.route('/', methods=['GET'])
@on_exception_result_failure
def n_queens_index(): 
  with get_redis_connection() as connection:
    algorithms_infos = get_algorithms_infos(connection)
    saved_jobs = get_saved_jobs(connection)
  benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
  return jsonify({
    "result": "success",
    "algorithms": benchmarkable_algorithms,
    "running_job": get_running_nqueens(saved_jobs),
    "problem_parameters": get_nqueens_parameters()
  })

@n_queens_page.route('/start', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def run():
  saved_jobs = get_saved_jobs()
  algorithm_name, n, run_as_benchmark, timeout = get_post_data()
  debug_level = get_post_debug_level()
  job = start_algorithm_on_nqueens(
    algorithm_name,
    n,
    run_as_benchmark,
    timeout,
    debug_level
  )
  save_job(
    job,
    algorithm_name,
    n,
    run_as_benchmark,
    timeout,
    saved_jobs
  )
  set_saved_jobs(saved_jobs)

@n_queens_page.route('/get_logs', methods=['POST'])
@on_exception_result_failure
def get_nqueens_logs():
  algorithm_name, n, run_as_benchmark, timeout = get_post_data()
  log_file_content = retrieve_log_file(algorithm_name, n, run_as_benchmark, timeout)
  return jsonify({ 'result': log_file_content})

@n_queens_page.route('/stop', methods=['POST'])
@on_exception_result_failure
def stop():
  saved_jobs = get_saved_jobs()
  algorithm_name, n, run_as_benchmark, timeout = get_post_data()
  if stop_job_nqueens(algorithm_name, n, run_as_benchmark, timeout, saved_jobs):
    set_saved_jobs(saved_jobs)
    return jsonify({'result': 'success'})
  return jsonify({'result': 'failure'})

@n_queens_page.route('/get_dimacs', methods=['POST'])
@on_exception_result_failure
def dimacs():
  n = get_post_N()
  dimacs_file = generate_nqueens_dimacs(int(n), generate_new=False)
  if dimacs_file is None:
    return jsonify(result="failure")
  return jsonify(
    result="success",
    content=get_benchmark_entry_content(NQUEENS_PROBLEM_NAME, f"{n}.cnf")
  )

@n_queens_page.route('/is_finished', methods=['POST'])
@on_exception_result_failure
def is_finished():
  algorithm_name, n, run_as_benchmark, timeout = get_post_data()
  is_finished, model = is_nqueens_finished(algorithm_name, n, run_as_benchmark, timeout)
  if is_finished:
    return jsonify(
      result="yes",
      model=model if not run_as_benchmark else []
    )
  else:
    return jsonify(result="no")
