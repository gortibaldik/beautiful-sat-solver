from logzero import logger
from satsolver.dpll.assignment import assign_true, unassign_multiple
from satsolver.dpll.representation import SATClause
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.representation import debug_str, lit_is_none, lit_is_satisfied
from satsolver.utils.stats import SATSolverStats
from typing import List

def find_not_assigned(clause: SATClause, itv, assignment):
  unassigned_lit_int = None
  at_least_one_true = False
  for lit_int in clause.children:
    if lit_is_none(lit_int, assignment):
      unassigned_lit_int = lit_int
      break
    if lit_is_satisfied(lit_int, assignment):
       at_least_one_true = True
    
  # conflict
  if unassigned_lit_int is None and not at_least_one_true:
    # logger.warning(f"{str(clause)} was expected to contain unassigned literal!")
    return UnitPropagationResult.CONFLICT

  return unassigned_lit_int

def find_unit_clause(
  c: List[SATClause], # clauses
  stats: SATSolverStats
):
  n_satisfied = 0
  result, unit_clauses = None, []
  for clause in c:
    stats.unitPropCheckedClauses += 1
    # clause is satisfied
    if clause.n_satisfied > 0:
      n_satisfied += 1
      continue
    if len(clause) == clause.n_unsatisfied:
      return UnitPropagationResult.CONFLICT, None
    # clause is unit
    if len(clause) - clause.n_unsatisfied == 1:
      result = UnitPropagationResult.UNIT_FOUND
      unit_clauses.append(clause)
  if result is not None:
    return result, unit_clauses
  if n_satisfied == len(c):
    return UnitPropagationResult.ALL_SATISFIED, None
  return UnitPropagationResult.NOTHING_FOUND, None

def unit_propagation(
  itv, # int to variable
  itc, # int to clauses
  assignment,
  cs,  # clauses to search
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    result, clauses = find_unit_clause(cs, stats)

    if result == UnitPropagationResult.CONFLICT:
      unassign_multiple(assigned_literals, assignment, itc, itv)
      return UnitPropagationResult.CONFLICT, []
    
    if clauses is None:
      continue

    for clause in clauses:
      lit_int = find_not_assigned(clause, itv, assignment)

      if lit_int is None:
        continue
      elif lit_int == UnitPropagationResult.CONFLICT:
        unassign_multiple(assigned_literals, assignment, itc, itv)
        return UnitPropagationResult.CONFLICT, []

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
