from typing import List

from satsolver.cdcl.representation import CDCLData


def vsids_array_dec_var_selection(
  data: CDCLData
):
  max_count = -1
  max_var_int = None
  for var_int, state in enumerate(data.assignment):
    if state is None:
      lit_int = var_int + var_int
      for i in range(2):
        count = data.vsids_activity[lit_int + i]
        if max_count < count:
          max_var_int = var_int
          max_count = count
  
  if max_var_int is None:
    raise RuntimeError("Each variable is assigned!")
  pos_lit_int = var_int + var_int
  if data.vsids_activity[pos_lit_int] >= data.vsids_activity[pos_lit_int + 1]:
    # positive literal should be taken as the first one
    return max_var_int, 2
  else:
    # negative literal should be taken as the first one
    return max_var_int, 1