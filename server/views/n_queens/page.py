from flask import Blueprint
from satsolver.task6 import NQUEENS_PROBLEM_NAME, generate_nqueens_dimacs
from server.get_running_job import construct_nqueens_index
from server.task_runner.nqueens import task_runner_start_algorithm_on_nqueens
from server.utils.exception_utils import (
  on_exception_result_failure,
  on_success_result_success,
)
from server.views.n_queens.utils import (
  get_entry_name,
  get_nqueens_parameters,
  get_running_nqueens,
  should_return_model,
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
    task_runner_start_algorithm_on_nqueens,
    construct_nqueens_index
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
    NQUEENS_PROBLEM_NAME,
    get_entry_name
  )

@n_queens_page.route('/is_finished', methods=['POST'])
@on_exception_result_failure
def is_finished():
  return get_progress(
    _post_data_array,
    construct_nqueens_index,
    should_return_model
  )
