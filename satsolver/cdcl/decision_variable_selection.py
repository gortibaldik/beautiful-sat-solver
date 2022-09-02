from satsolver.cdcl.representation import CDCLData

def dec_var_selection(
  data: CDCLData
):
  """
  Select first unassigned variable
  """
  for i in data.order_of_vars:
    if data.assignment[i] is None:
      return i
  raise RuntimeError("Each variable is assigned!")