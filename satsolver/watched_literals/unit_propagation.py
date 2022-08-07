from logzero import logger
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.assignment import assign_true, get_literal_int, unassign_multiple
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

def find_unit_clauses(
  c: List[Tuple[SATClause, int]], # clauses
  stats: SATSolverStats
):
  result: UnitPropagationResult = None
  unit_clauses: List[Tuple[SATClause, int]] = []
  for clause, watched_index in c:
    stats.unitPropCheckedClauses += 1
    # satisfied clause
    if clause.get_w(0).is_satisfied():
      continue

    # unit clause, because there is single literal in the clause
    if clause.watched[1] is None:
      unit_clauses.append((clause, 0))
      result = UnitPropagationResult.UNIT_FOUND
      continue

    # satisfied clause
    # clause.watched[1] is not None
    if clause.get_w(1).is_satisfied():
      continue

    # if 0-th watched literal is False, it is because there is
    # no other literal in the clause which is unassigned and
    # isn't the second watched literal
    #
    # if second watched literal is None, it means the clause
    # is unit
    #
    # analogically for the other side
    if clause.get_w(0).is_unsatisfied() and not clause.get_w(1).is_assigned():
      unit_clauses.append((clause, 1))
      result = UnitPropagationResult.UNIT_FOUND
    if clause.get_w(1).is_unsatisfied() and not clause.get_w(0).is_assigned():
      unit_clauses.append((clause, 0))
      result = UnitPropagationResult.UNIT_FOUND

    if clause.get_w(0).is_unsatisfied() and clause.get_w(1).is_unsatisfied():
      return UnitPropagationResult.CONFLICT, None

  if result is not None:
    return result, unit_clauses

  return UnitPropagationResult.NOTHING_FOUND, []

def unit_propagation(
  itc, # int to clauses
  cs,  # clauses to search
  ca,  # all clauses
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    result, clauses = find_unit_clauses(cs, stats)

    if result == UnitPropagationResult.CONFLICT:
      unassign_multiple(assigned_literals, itc)
      return UnitPropagationResult.CONFLICT, []

    # implicitly result == (UnitPropagationResult.NOTHING_FOUND or UnitPropagationResult.UNIT_FOUND)
    for clause, n_of_wl in clauses:
      literal = clause.get_w(n_of_wl)

      if literal.is_satisfied():
        continue
      # literal is not True and is assigned => it is false
      # hence we have a conflict
      elif literal.is_assigned():
        unassign_multiple(assigned_literals, itc)
        return UnitPropagationResult.CONFLICT, []


      assign_true(
        literal,
        itc,
        assigned_literals
      )
      stats.unitProps += 1
      lit_int, other_int = get_literal_int(literal)
      list_of_cs.append(itc[other_int])

  return UnitPropagationResult.NOTHING_FOUND, assigned_literals
