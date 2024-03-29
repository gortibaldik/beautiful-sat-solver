import satsolver.utils.general_setup as general_setup

from argparse import ArgumentParser
from satsolver.dpll.assignment import assign_true, unassign, unassign_multiple
from satsolver.dpll.decision_variable_selection import dec_var_selection
from satsolver.dpll.dpll import DPLL
from satsolver.dpll.dpll_iter import DPLLIter
from satsolver.dpll.structures_preparation import health_check, prepare_structures
from satsolver.dpll.unit_propagation import unit_propagation

def get_info(argumentParser: ArgumentParser=None):
  return general_setup.get_info(
    name="DPLL.v5",
    taskName="TASK 2",
    benchmarkable=True,
    symbol="cat",
    argumentParser=argumentParser,
    options=[general_setup.create_option(
      name="iterative",
      type=general_setup.TypeOfOption.CHECKBOX,
      default=False,
      hint="Whether to use iterative version of the algorithm or the recursive one"
    )]
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True,
  iterative=False
):
  if iterative:
    dpll = DPLLIter(
      prepare_structures=prepare_structures,
      unit_propagation=unit_propagation,
      dec_var_selection=dec_var_selection,
      assign_true=assign_true,
      unassign=unassign,
      unassign_multiple=unassign_multiple
    )
  else:
    dpll = DPLL(
      prepare_structures=prepare_structures,
      unit_propagation=unit_propagation,
      dec_var_selection=dec_var_selection,
      assign_true=assign_true,
      unassign=unassign,
      unassign_multiple=unassign_multiple
    )
  dpll.health_check = health_check
  return general_setup.find_model(
    dpll.dpll,
    input_file=input_file,
    warning=warning,
    debug=debug,
    output_to_stdout=output_to_stdout,
    nnf_reduce_implications=nnf_reduce_implications
  )

if __name__ == "__main__":
  parser = general_setup.create_parser()
  get_info(parser)
  args = parser.parse_args()
  print(vars(args))
  find_model(
    **vars(args)
  )

