from logzero import logger
from satsolver.dpll.assignment import assign_true, get_literal_int, unassign_multiple
from satsolver.dpll.representation import SATClause
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.stats import SATSolverStats
from typing import List

def find_not_assigned(clause: SATClause):
  unassigned_literal = None
  at_least_one_true = False
  for literal in clause.children:
    if literal.satVariable.truth_value is None:
      unassigned_literal = literal
      break
    if literal.satVariable.truth_value == literal.positive:
       at_least_one_true = True
    
  # conflict
  if unassigned_literal is None and not at_least_one_true:
    # logger.warning(f"{str(clause)} was expected to contain unassigned literal!")
    return UnitPropagationResult.CONFLICT

  return unassigned_literal

def find_unit_clause(
  c: List[SATClause] # clauses
):
  n_satisfied = 0
  result, unit_clauses = None, []
  for clause in c:
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
  itc, # int to clauses
  cs,  # clauses to search
  ca,  # all clauses
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    result, clauses = find_unit_clause(cs)

    if result == UnitPropagationResult.CONFLICT:
      unassign_multiple(assigned_literals, itc)
      return UnitPropagationResult.CONFLICT, []
    
    if clauses is None:
      continue

    for clause in clauses:
      literal = find_not_assigned(clause)

      if literal is None:
        continue
      elif literal == UnitPropagationResult.CONFLICT:
        unassign_multiple(assigned_literals, itc)
        return UnitPropagationResult.CONFLICT, []

      assign_true(
        literal,
        itc,
        assigned_literals
      )
      stats.unitProps += 1
      lit_int, other_int, _ = get_literal_int(literal)
      list_of_cs.append(itc[other_int])

  return UnitPropagationResult.NOTHING_FOUND, assigned_literals
