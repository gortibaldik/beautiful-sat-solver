from flask import Blueprint
from satsolver.task6 import NQUEENS_PROBLEM_NAME, generate_nqueens_dimacs
from server.get_running_job import construct_nqueens_index
from server.models.nqueens import create_n_commit_nqueens
from server.utils.exception_utils import (
  on_exception_result_failure,
  on_success_result_success,
)
from server.views.n_queens.utils import (
  ensure_nqueens_storage_file,
  get_nqueens_benchmark_next,
  get_nqueens_benchmark_start,
  get_nqueens_parameters,
  get_nqueens_start_log,
  get_running_nqueens,
  is_nqueens_benchmark_finished,
  is_nqueens_satisfiable,
  shouldnt_return_model,
)
from server.views.problem_prototype.page import (
  dimacs,
  get_logs,
  get_progress,
  index,
  start,
  stop
)

n_queens_page = Blueprint('n_queens_page', __name__)
_post_data_array = ['algorithm', 'N', 'run_as_benchmark', 'timeout']

@n_queens_page.route('/', methods=['GET'])
@on_exception_result_failure
def n_queens_index():
  return index(get_running_nqueens, get_nqueens_parameters)

@n_queens_page.route('/start', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def start_nqueens():
  start(
    _post_data_array,
    get_nqueens_start_log,
    generate_nqueens_dimacs,
    is_nqueens_satisfiable,
    create_n_commit_nqueens,
    ensure_nqueens_storage_file,
    construct_nqueens_index,
    get_benchmark_start=get_nqueens_benchmark_start,
    get_benchmark_next=get_nqueens_benchmark_next,
    is_benchmark_finished=is_nqueens_benchmark_finished
  )

@n_queens_page.route('/get_logs', methods=['POST'])
@on_exception_result_failure
def get_nqueens_logs():
  return get_logs(
    _post_data_array,
    construct_nqueens_index
  )

@n_queens_page.route('/stop', methods=['POST'])
@on_exception_result_failure
def stop_nqueens():
  return stop(
    _post_data_array,
    construct_nqueens_index
  )

@n_queens_page.route('/get_dimacs', methods=['POST'])
@on_exception_result_failure
def dimacs_nqueens():
  return dimacs(
    _post_data_array,
    generate_nqueens_dimacs,
    NQUEENS_PROBLEM_NAME
  )

@n_queens_page.route('/is_finished', methods=['POST'])
@on_exception_result_failure
def is_finished():
  return get_progress(
    _post_data_array,
    construct_nqueens_index,
    shouldnt_return_model
  )
