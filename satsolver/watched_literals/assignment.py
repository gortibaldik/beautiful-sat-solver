from logzero import logger
from satsolver.utils.representation import debug_str, lit_is_assigned
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

def assign_true(
  lit_int: int,
  itv,
  assignment,
  itc: List[List[Tuple[SATClause, int]]], # int to clauses
  assigned_literals=None
):
  vix = lit_int >> 1
  if assignment[vix] is not None:
    raise RuntimeError(f"`{debug_str(lit_int, itv)}` was supposed to be unassigned!")
  if assigned_literals is not None:
    assigned_literals.append(lit_int)

  # satisfy lit_int
  assignment[vix] = (lit_int & 1) ^ 1

  # we do not have to do anything with positive_clauses
  # watched literal in these clauses needs to remain on
  # positive literal
  
  # in all negative clauses where the literal is watched
  # we need to move the reference to an unassigned literal
  # since the watched literal is now false
  negative_clauses = itc[lit_int ^ 1]
  clauses_to_keep = []
  for entry in negative_clauses:
    clause, watched_index = entry

    # index of the second watched literal
    swli = clause.watched[watched_index ^ 1]

    # watched literal index
    wli = clause.watched[watched_index]
    len_clause = len(clause)

    # if second watched literal is already satisfied there is no
    # work to do
    #
    # if second watched literal is false, there isn't any
    # other unassigned literal in the clause
    if lit_is_assigned(clause[swli], assignment):
      clauses_to_keep.append(entry)
      continue

    # find new watched literal for the clause
    for i, c_lit in enumerate(clause.children):
      if i == wli or i == swli:
        continue
      
      # candidate literal c_lit
      a_c = assignment[c_lit >> 1]
      if a_c is None or a_c != (c_lit & 1):
        itc[c_lit].append(entry)
        clause.watched[watched_index] = i
        break
    else:
      clauses_to_keep.append(entry)

  # until this assignment the data structures are in inconsistent
  # state
  itc[lit_int ^ 1] = clauses_to_keep

def unassign(
  lit_int: int,
  assignment,
  itc: List[List[SATClause]], # int to clauses
  itv: List[str]
):
  vix = lit_int >> 1
  if assignment[vix] is None:
    raise RuntimeError(f"`{debug_str(lit_int)}` was supposed to be assigned!")

  assignment[vix] = None

def unassign_multiple(
  ls: List[int],
  assignment,
  itc: List[List[SATClause]],
  itv: List[str]
):
  for l in ls:
    unassign(l, assignment, itc, itv)
