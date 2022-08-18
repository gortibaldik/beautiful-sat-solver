from satsolver.utils.representation import debug_str
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

_def_dec_lvl = (-1, -1)

def unassign(
  lit_int: int,
  assignment,
  dec_lvls_of_vars,
  itc: List[List[SATClause]], # int to clauses
  itv: List[str]
):
  vix = lit_int >> 1
  if assignment[vix] is None:
    raise RuntimeError(f"`{debug_str(lit_int, itv)}` was supposed to be assigned!")

  assignment[vix] = None
  dec_lvls_of_vars[vix] = _def_dec_lvl

def unassign_multiple(
  ls: List[int],
  assignment: List[int],
  dec_lvls_of_vars: List[Tuple[int, int]],
  itc: List[List[SATClause]],
  itv: List[str]
):
  for lit_int in ls:
    vix = lit_int >> 1
    if assignment[vix] is None:
      raise RuntimeError(f"`{debug_str(lit_int, itv)}` was supposed to be assigned!")

    assignment[vix] = None
    dec_lvls_of_vars[vix] = _def_dec_lvl