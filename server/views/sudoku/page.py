from flask import Blueprint
from satsolver.task7 import SUDOKU_PROBLEM_NAME, generate_sudoku_dimacs
from server.get_running_job import construct_sudoku_index
from server.utils.exception_utils import (
  on_exception_result_failure,
  on_success_result_success,
)
from server.views.problem_prototype.page import (
  dimacs,
  get_logs,
  get_progress,
  index,
  start,
  stop
)
from server.views.sudoku.sudoku_generator.sudoku_generator import SudokuDifficulty, generate_sudoku
from server.views.sudoku.utils import (
  create_n_commit_sudoku,
  ensure_sudoku_storage_file,
  get_difficulty,
  get_running_sudoku,
  get_sudoku_parameters,
  get_sudoku_start_log,
  is_sudoku_satisfiable,
  shouldnt_return_model
)

sudoku_page = Blueprint('sudoku_page', __name__)
_start_data_array = ['algorithm', 'sudoku']
_post_data_array = ['algorithm']
_dimacs_data_array = ['sudoku']

@sudoku_page.route('/', methods=['GET'])
@on_exception_result_failure
def sudoku_index():
  return index(get_running_sudoku, get_sudoku_parameters)

@sudoku_page.route('/start', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def start_sudoku():
  start(
    _start_data_array,
    get_sudoku_start_log,
    generate_sudoku_dimacs,
    is_sudoku_satisfiable,
    create_n_commit_sudoku,
    ensure_sudoku_storage_file,
    construct_sudoku_index
  )

@sudoku_page.route('/get_logs', methods=['POST'])
@on_exception_result_failure
def get_sudoku_logs():
  return get_logs(
    _post_data_array,
    construct_sudoku_index
  )

@sudoku_page.route('/stop', methods=['POST'])
@on_exception_result_failure
def stop_sudoku():
  return stop(
    _post_data_array,
    construct_sudoku_index
  )

@sudoku_page.route('/get_dimacs', methods=['POST'])
@on_exception_result_failure
def dimacs_sudoku():
  return dimacs(
    _dimacs_data_array,
    generate_sudoku_dimacs,
    SUDOKU_PROBLEM_NAME
  )

@sudoku_page.route('/is_finished', methods=['POST'])
@on_exception_result_failure
def is_finished():
  return get_progress(
    _post_data_array,
    construct_sudoku_index,
    shouldnt_return_model
  )

@sudoku_page.route('/generate', methods=['POST'])
@on_exception_result_failure
def generate():
  difficulty = get_difficulty()
  initial, final = generate_sudoku(SudokuDifficulty(difficulty))
  return { "board": str(final)}
