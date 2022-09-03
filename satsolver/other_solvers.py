import satsolver.utils.general_setup as general_setup

from argparse import ArgumentParser
from satsolver.wrappers.solver_wrapper import CADICAL, GLUCOSE_SOLVER, LINGELING, MINISAT, solve

def get_info(argumentParser: ArgumentParser=None):
  return general_setup.get_info(
    name="other_solver",
    taskName="TASK 6",
    benchmarkable=True,
    symbol="spider",
    argumentParser=argumentParser,
    options=[general_setup.create_option(
      name="solver_name",
      type=general_setup.TypeOfOption.LIST,
      default=GLUCOSE_SOLVER,
      hint="Which solver to use",
      options=[
        GLUCOSE_SOLVER,
        MINISAT,
        LINGELING,
        CADICAL
      ]
    )]
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True,
  **kwargs
):
  return general_setup.find_model(
    solve,
    input_file=input_file,
    warning=warning,
    debug=debug,
    output_to_stdout=output_to_stdout,
    nnf_reduce_implications=nnf_reduce_implications,
    **kwargs
  )
