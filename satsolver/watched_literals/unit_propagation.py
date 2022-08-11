from logzero import logger
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.assignment import assign_true, unassign_multiple
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

def find_unit_clauses(
  itv: List[str], # int to variable
  c: List[Tuple[SATClause, int]], # clauses
  assignment: List[bool],
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
    lit_w = clause.get_w(watched_index)
    a_w = assignment[lit_w >> 1]
    if a_w == ((lit_w & 1) ^ 1):
      continue

    lit_o = clause.get_w(watched_index ^ 1)
    a_o = assignment[lit_o >> 1]
    if a_o == ((lit_o & 1) ^ 1):
      continue

    # assignment => watched literal in clause becomes False
    # => new literal is found
    # => if it is unsatisfied then it means that the clause is either
    # unit of conflict
    if a_w is not None:
      if a_o is None:
        unit_clauses.append((clause, watched_index ^ 1))
      else:
        return UnitPropagationResult.CONFLICT, None

  if len(unit_clauses) > 0:
    return UnitPropagationResult.UNIT_FOUND, unit_clauses

  return UnitPropagationResult.NOTHING_FOUND, unit_clauses

def unit_propagation(
  itv, # int to variables
  itc, # int to clauses
  assignment,
  cs,  # clauses to search
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    result, clauses = find_unit_clauses(itv, cs, assignment, stats)

    if result == UnitPropagationResult.CONFLICT:
      unassign_multiple(assigned_literals, assignment, itc, itv)
      return UnitPropagationResult.CONFLICT, []

    # implicitly result == (UnitPropagationResult.NOTHING_FOUND or UnitPropagationResult.UNIT_FOUND)
    for clause, n_of_wl in clauses:
      lit_int = clause.get_w(n_of_wl)
      a_l = assignment[lit_int >> 1]

      # is unsatisfied
      if a_l == (lit_int & 1):
        unassign_multiple(assigned_literals, assignment, itc, itv)
        return UnitPropagationResult.CONFLICT, []

      # is satisfied (not unsatisfied and not None)
      if a_l is not None:
        continue

      assign_true(
        lit_int,
        itv,
        assignment,
        itc,
        assigned_literals
      )
      stats.unitProps += 1
      list_of_cs.append(itc[lit_int ^ 1])

  return UnitPropagationResult.NOTHING_FOUND, assigned_literals
