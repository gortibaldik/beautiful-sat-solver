from typing import List

# TODO
def dec_var_selection(
  assignment: List[bool], # int to literal
):
  """
  Select first unassigned variable
  """
  for i, v in enumerate(assignment):
    if v is None:
      return i
  raise RuntimeError("Each variable is assigned!")