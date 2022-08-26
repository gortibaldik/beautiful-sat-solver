from satsolver.cdcl.representation import CDCLData

def dec_var_selection_static_sum(
  data: CDCLData
):
  """
  Select first unassigned variable in order of data.order_of_vars
  """
  for i in data.order_of_vars:
    if data.assignment[i] is None:
      return i, 2
  raise RuntimeError("Each variable is assigned!")

def dec_var_selection_basic(
  data: CDCLData
):
  """
  Select first unassigned variable
  """
  for i, v in enumerate(data.assignment):
    if v is None:
      return i, 2
  raise RuntimeError("Each variable is assigned!")