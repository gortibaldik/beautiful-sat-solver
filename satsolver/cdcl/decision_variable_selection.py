from satsolver.cdcl.representation import CDCLData

def add_assumptions(data: CDCLData):
  if data.assumptions is not None:
    for a in data.assumptions:
      var_int = a >> 1
      if data.assignment[var_int] is None:
        negativity = 5 - (a & 1) ^ 1
        return var_int, negativity
  return None

def dec_var_selection_static_sum(
  data: CDCLData
):
  """
  Select first unassigned variable in order of data.order_of_vars
  """
  result = add_assumptions(data)
  if result is not None:
    return result
  for i in data.order_of_vars:
    if data.assignment[i] is None:
      if data.negative_first:
        return i, 1
      else:
        return i, 2
  raise RuntimeError("Each variable is assigned!")

def dec_var_selection_basic(
  data: CDCLData
):
  """
  Select first unassigned variable
  """
  result = add_assumptions(data)
  if result is not None:
    return result
  for i, v in enumerate(data.assignment):
    if v is None:
      if data.negative_first:
        return i, 1
      else:
        return i, 2
  raise RuntimeError("Each variable is assigned!")