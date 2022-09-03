from flask import request
from satsolver.utils.general_setup import TypeOfOption, create_option
from server.get_running_job import RunningJobType, find_running_job

def get_running_nqueens(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result != RunningJobType.NQUEENS:
    return { "algorithm": "none" }
  else:
    algo, problem, descr1, descr2 = key.split(",")
    run_as_benchmark = descr1 == "benchmark"
    N = 8
    timeout = 30
    if not run_as_benchmark:
      N = int(descr1)
    else:
      timeout = int(descr2)
    return {
      "algorithm": algo,
      "run_as_benchmark": run_as_benchmark,
      "N":         N,
      "timeout":   timeout
    }

def get_nqueens_parameters():
  return [
    create_option(
      name="N",
      hint="Number of queens to place, size of the board",
      type=TypeOfOption.VALUE,
      default=8
    ),
    create_option(
      name="run_as_benchmark",
      hint="If checked, the selected algorithm runs for increasing N (1, 2, 3...) " +\
        "and stops when timeout is reached (e.g. if the algorithm runs more than T " +\
        " seconds for N=n then that run is interrupted and the suite is ended)",
      type=TypeOfOption.CHECKBOX,
      default=False
    ),
    create_option(
      name="timeout",
      hint="How many SECONDS the algorithm should run before abort",
      type=TypeOfOption.VALUE,
      default=30
    )
  ]

def get_post_N():
  post_data = request.get_json()
  N = post_data.get('N')
  return N

def should_return_model(**kwargs):
  return kwargs['run_as_benchmark']

def get_entry_name(**kwargs):
  return f"{kwargs['N']}.cnf"
