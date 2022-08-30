
from argparse import ArgumentParser
from satsolver.cdcl.assignment import unassign, unassign_multiple
from satsolver.cdcl.cdcl import CDCL
from satsolver.cdcl.conflict_analysis import conflict_analysis
from satsolver.cdcl.unit_propagation import unit_propagation
import satsolver.utils.general_setup as general_setup
from satsolver.watched_literals.assignment import assign_true
from satsolver.watched_literals.structures_preparation import prepare_structures

def get_info(argumentParser: ArgumentParser=None):
  return general_setup.get_info(
    name="CDCL.v5.1",
    taskName="TASK 4",
    benchmarkable=True,
    symbol="dove",
    argumentParser=argumentParser,
    options=[
      general_setup.create_option(
        name="conflict_limit_restarts",
        hint="Tested values: 32, with luby/restarts",
        type=general_setup.TypeOfOption.VALUE,
        default="32" 
      ),
      general_setup.create_option(
        name="conflict_limit_deletion",
        type=general_setup.TypeOfOption.VALUE,
        default="200"
      ),
      general_setup.create_option(
        name="use_restarts",
        type=general_setup.TypeOfOption.CHECKBOX,
        default=False
      ),
      general_setup.create_option(
        name="use_luby",
        type=general_setup.TypeOfOption.CHECKBOX,
        default=True
      ),
      general_setup.create_option(
        name="dec_var_heuristic",
        type=general_setup.TypeOfOption.LIST,
        default="Static Sum",
        options=[
          "No Heuristic",
          "Static Sum"
        ]
      ),
      general_setup.create_option(
        name="negative_first",
        type=general_setup.TypeOfOption.CHECKBOX,
        default=False,
        hint="Whether to take negative literal as first during decision variable selection"
      )
    ]
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
  cdcl = CDCL(
    prepare_structures=prepare_structures,
    unit_propagation=unit_propagation,
    assign_true=assign_true,
    unassign=unassign,
    unassign_multiple=unassign_multiple,
    conflict_analysis=conflict_analysis
  )
  return general_setup.find_model(
    cdcl.cdcl,
    input_file=input_file,
    warning=warning,
    debug=debug,
    output_to_stdout=output_to_stdout,
    nnf_reduce_implications=nnf_reduce_implications,
    **kwargs
  )

if __name__ == "__main__":
  parser = general_setup.create_parser()
  get_info(parser)
  args = parser.parse_args()
  print(vars(args))
  find_model(
    **vars(args)
  )

