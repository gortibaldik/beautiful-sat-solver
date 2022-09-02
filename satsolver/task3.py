from satsolver.dpll.decision_variable_selection import dec_var_selection
from satsolver.dpll.dpll import DPLL
import satsolver.utils.general_setup as general_setup
from satsolver.watched_literals.assignment import assign_true, unassign, unassign_multiple
from satsolver.watched_literals.structures_preparation import prepare_structures
from satsolver.watched_literals.unit_propagation import unit_propagation

def get_info():
  return general_setup.get_info(
    name="Watched Literals.v6",
    taskName="TASK 3",
    benchmarkable=True,
    symbol="crow"
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True
):
  dpll = DPLL(
    prepare_structures=prepare_structures,
    unit_propagation=unit_propagation,
    dec_var_selection=dec_var_selection,
    assign_true=assign_true,
    unassign=unassign,
    unassign_multiple=unassign_multiple,
  )
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
  args = parser.parse_args()
  find_model(
    input_file=args.input_file,
    warning=args.warning,
    debug=args.debug,
    output_to_stdout=args.output_to_stdout
  )
