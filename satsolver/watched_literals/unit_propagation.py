from logzero import logger
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.assignment import assign_true, get_literal_int, unassign_multiple
from satsolver.watched_literals.representation import SATClause, lit_is_none, lit_is_satisfied, lit_is_unsatisfied
from typing import List, Tuple

# TODO
def find_unit_clauses(
  c: List[Tuple[SATClause, int]], # clauses
  assignment,
  stats: SATSolverStats
):
  unit_clauses: List[Tuple[SATClause, int]] = []
  for entry in c:
    clause, watched_index = entry
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
    if lit_is_satisfied(clause.get_w(0), assignment) or lit_is_satisfied(clause.get_w(1), assignment):
      continue

    # assignment => watched literal in clause becomes False
    # => new literal is found
    # => if it is unsatisfied then it means that the clause is either
    # unit of conflict
    if lit_is_unsatisfied(clause.get_w(watched_index), assignment):
      other_watched = watched_index ^ 1
      if lit_is_none(clause.get_w(other_watched), assignment):
        unit_clauses.append((clause, other_watched))
      else:
        return UnitPropagationResult.CONFLICT, None

  if len(unit_clauses) > 0:
    return UnitPropagationResult.UNIT_FOUND, unit_clauses

  return UnitPropagationResult.NOTHING_FOUND, unit_clauses

def unit_propagation(
  itc, # int to clauses
  assignment,
  cs,  # clauses to search
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    result, clauses = find_unit_clauses(cs, assignment, stats)

    if result == UnitPropagationResult.CONFLICT:
      unassign_multiple(assigned_literals, assignment, itc)
      return UnitPropagationResult.CONFLICT, []

    # implicitly result == (UnitPropagationResult.NOTHING_FOUND or UnitPropagationResult.UNIT_FOUND)
    for clause, n_of_wl in clauses:
      lit_int = clause.get_w(n_of_wl)

      if lit_is_satisfied(lit_int, assignment):
        continue

      elif lit_is_unsatisfied(lit_int, assignment):
        unassign_multiple(assigned_literals, assignment, itc)
        return UnitPropagationResult.CONFLICT, []

      assign_true(
        lit_int,
        assignment,
        itc,
        assigned_literals
      )
      stats.unitProps += 1
      list_of_cs.append(itc[lit_int ^ 1])

  return UnitPropagationResult.NOTHING_FOUND, assigned_literals
