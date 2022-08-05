import satsolver.utils.general_setup as general_setup

from satsolver.dpll.dpll import dpll

def get_info():
  return general_setup.get_info(
    name="DPLL.v2",
    taskName="TASK 2",
    benchmarkable=True
  )

def find_model(
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True
):
  return general_setup.find_model(
    dpll,
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
