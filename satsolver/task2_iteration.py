from satsolver.dpll.assignment import assign_true, unassign, unassign_multiple
from satsolver.dpll.decision_variable_selection import dec_var_selection
from satsolver.dpll.structures_preparation import health_check, prepare_structures
from satsolver.dpll.unit_propagation import unit_propagation
import satsolver.utils.general_setup as general_setup

from satsolver.dpll.dpll_iter import DPLLIter

def get_info():
  return general_setup.get_info(
    name="DPLL.v5.iter",
    taskName="TASK 2 - iter",
    benchmarkable=True,
    symbol="cat"
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True
):
  dpll = DPLLIter(
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
  args = parser.parse_args()
  find_model(
      input_file=args.input_file,
      warning=args.warning,
      debug=args.debug,
      output_to_stdout=args.output_to_stdout
  )
