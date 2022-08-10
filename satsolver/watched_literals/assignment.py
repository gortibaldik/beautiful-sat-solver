from logzero import logger
from satsolver.watched_literals.representation import SATClause, SATLiteral, debug_str, lit_is_assigned, lit_is_none, lit_is_satisfied, satisfy_lit, unassign_lit
from satsolver.utils.structures_preparation import get_literal_int
from typing import List, Tuple

# TODO
def assign_true(
  lit_int: int,
  assignment,
  itc: List[List[Tuple[SATClause, int]]], # int to clauses
  assigned_literals=None
):
  if lit_is_assigned(lit_int, assignment):
    raise RuntimeError(f"`{debug_str(lit_int)}` was supposed to be unassigned!")
  if assigned_literals is not None:
    assigned_literals.append(lit_int)
  satisfy_lit(lit_int, assignment)

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
    second_watched_literal_index = clause.watched[watched_index ^ 1]

    # watched literal index
    wli = clause.watched[watched_index]
    len_clause = len(clause)

    # if second watched literal is already satisfied there is no
    # work to do
    #
    # if second watched literal is false, there isn't any
    # other unassigned literal in the clause
    if lit_is_assigned(clause[second_watched_literal_index], assignment):
      clauses_to_keep.append(entry)
      continue

    # find new watched literal for the clause
    found_new_watched = False
    for _ in range(1, len_clause):
      wli += 1
      if wli == len_clause:
        wli = 0
      if wli == second_watched_literal_index:
        continue
      candidate_lit_int = clause[wli]
      if lit_is_none(candidate_lit_int, assignment) or lit_is_satisfied(candidate_lit_int, assignment):
        found_new_watched = True
        itc[lit_int].append(entry)
        clause.watched[watched_index] = wli
        break
    
    if not found_new_watched:
      clauses_to_keep.append(entry)

  # until this assignment the data structures are in inconsistent
  # state
  itc[lit_int ^ 1] = clauses_to_keep

def unassign(
  lit_int: int,
  assignment,
  itc: List[List[SATClause]], # int to clauses
):
  if lit_is_none(lit_int, assignment):
    raise RuntimeError(f"`{debug_str(lit_int)}` was supposed to be assigned!")

  unassign_lit(lit_int, assignment)

def unassign_multiple(
  ls: List[SATLiteral],
  assignment,
  itc: List[List[SATClause]]
):
  for l in ls:
    unassign(l, assignment, itc)
