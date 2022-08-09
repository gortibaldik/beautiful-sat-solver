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
  unit_clauses: List[Tuple[SATClause, int]] = []
  for clause, watched_index in c:
    stats.unitPropCheckedClauses += 1

    if watched_index == -1:
      # only in the initial unit propagation we traverse
      # a list where watched_index == -1, therefore there
      # we only need to check for real unit clauses (only
      # one literal clauses)
      if clause.watched[1] is None:
        unit_clauses.append((clause, 0))
        continue
      continue
      
    # satisfied clause
    if clause.get_w(0).is_satisfied() or clause.get_w(1).is_satisfied():
      continue

    # assignment => watched literal in clause becomes False
    # => new literal is found
    # => if it is unsatisfied then it means that the clause is either
    # unit of conflict
    if clause.get_w(watched_index).is_unsatisfied():
      other_watched = 0 if watched_index == 1 else 1
      if not clause.get_w(other_watched).is_assigned():
        unit_clauses.append((clause, other_watched))
      else:
        return UnitPropagationResult.CONFLICT, None

  if len(unit_clauses) > 0:
    return UnitPropagationResult.UNIT_FOUND, unit_clauses

  return UnitPropagationResult.NOTHING_FOUND, unit_clauses

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
