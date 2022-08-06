from satsolver.watched_literals.representation import SATClause, SATLiteral
from satsolver.utils.structures_preparation import get_literal_int
from typing import List, Tuple

def assign_true(
  literal: SATLiteral,
  itc: List[List[Tuple[SATClause, int]]], # int to clauses
  assigned_literals=[]
):
  if literal.is_assigned():
    raise RuntimeError(f"`{str(literal)}` was supposed to be unassigned!")
  assigned_literals.append(literal)
  lit_int, other_int = get_literal_int(literal)
  literal.satisfy()

  # we do not have to do anything with positive_clauses
  # watched literal in these clauses needs to remain on
  # positive literal
  
  # in all negative clauses where the literal is watched
  # we need to move the reference to an unassigned literal
  # since the watched literal is now false
  negative_clauses = itc[other_int]
  clauses_to_keep = []
  for clause, watched_index in negative_clauses:
    other_watched_index = (watched_index + 1) % 2

    # index of the second watched literal
    second_watched_literal_index = clause.watched[other_watched_index]
    watched_literal_index = clause.watched[watched_index]
    len_clause = len(clause)

    # if second watched literal is already satisfied there is no
    # work to do
    #
    # if second watched literal is false, there isn't any
    # other unassigned literal in the clause
    if clause[second_watched_literal_index].is_assigned():
      clauses_to_keep.append((clause, watched_index))
      continue

    # find new watched literal for the clause
    for i in range(1, len_clause):
      j = (i + watched_literal_index) % len_clause
      if j == second_watched_literal_index:
        continue
      if not clause[j].is_assigned():
        candidate_literal = clause[j]
        pos_int, _ = get_literal_int(candidate_literal)
        itc[pos_int].append((clause, watched_index))
        clause.watched[watched_index] = j
        break

  # until this assignment the data structures are in inconsistent
  # state
  itc[other_int] = clauses_to_keep

def unassign(
  literal: SATLiteral,
  itc: List[List[SATClause]], # int to clauses
):
  if not literal.is_assigned():
    raise RuntimeError(f"`{str(literal)}` was supposed to be assigned!")

  literal.unassign()

def unassign_multiple(
  ls: List[SATLiteral],
  itc: List[List[SATClause]]
):
  for l in ls:
    unassign(l, itc)
