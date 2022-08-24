
from satsolver.cdcl.assignment import unassign, unassign_multiple
from satsolver.cdcl.cdcl import CDCL
from satsolver.cdcl.conflict_analysis import conflict_analysis
from satsolver.cdcl.unit_propagation import unit_propagation
from satsolver.dpll.decision_variable_selection import dec_var_selection
import satsolver.utils.general_setup as general_setup
from satsolver.watched_literals.assignment import assign_true
from satsolver.watched_literals.structures_preparation import prepare_structures

def get_info():
  return general_setup.get_info(
    name="CDCL.v3.r200.lbd3",
    taskName="TASK 4",
    benchmarkable=True,
    symbol="dove"
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True
):
  cdcl = CDCL(
    prepare_structures=prepare_structures,
    unit_propagation=unit_propagation,
    dec_var_selection=dec_var_selection,
    assign_true=assign_true,
    unassign=unassign,
    unassign_multiple=unassign_multiple,
    conflict_analysis=conflict_analysis
  )
  return general_setup.find_model(
    cdcl.cdcl_r200_lbd3,
    input_file=input_file,
    warning=warning,
    debug=debug,
    output_to_stdout=output_to_stdout,
    nnf_reduce_implications=nnf_reduce_implications
  )

if __name__ == "__main__":
  parser = general_setup.create_parser()
  args = parser.parse_args()
  find_model(
    input_file=args.input_file,
    warning=args.warning,
    debug=args.debug,
    output_to_stdout=args.output_to_stdout
  )
