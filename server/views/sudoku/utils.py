from flask import request
from satsolver.utils.general_setup import TypeOfOption, create_option
from server.get_running_job import RunningJobType, find_running_job
from server.task_runner.utils import ensure_storage_file

def get_running_sudoku(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result != RunningJobType.SUDOKU:
    return { "algorithm": "none" }
  else:
    algo, _, _, _ = key.split(",")
    return {
      "algorithm": algo
    }

def get_sudoku_parameters():
  return [
    create_option(
      name="Sudoku",
      hint="Sudoku to solve",
      type=TypeOfOption.MULTILINE_VALUE,
      default=""
    ),
    create_option(
      name="difficulty",
      hint="Difficulty of generated sudoku",
      type=TypeOfOption.LIST,
      default="easy",
      options=[
        "easy",
        "medium",
        "hard",
        "extreme"
      ]
    )
  ]

def get_entry_name(**kwargs):
  return f"sudoku.cnf"

def get_difficulty():
  d = request.get_json().get("difficulty", None)
  if d is None:
    raise RuntimeError("Not specified difficulty!")
  return d

def get_sudoku_start_log(sudoku, **kwargs):
  return f"sudoku: " + "- \n" + sudoku + "\n -"

def shouldnt_return_model(**kwargs):
  return False

def is_sudoku_satisfiable(**kwargs):
  return True

def ensure_sudoku_storage_file(algorithm):
  return ensure_storage_file(algorithm, "__sudoku__")

# no db storing results for sudoku
def create_n_commit_sudoku(**kwargs):
  pass
