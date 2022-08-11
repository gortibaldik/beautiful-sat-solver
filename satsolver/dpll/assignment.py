from satsolver.dpll.representation import SATClause
from satsolver.utils.representation import SATLiteral
from satsolver.utils.enums import UnitPropagationResult
from typing import List

def get_literal_int(literal: SATLiteral):
  is_positive = literal.positive
  if is_positive:
    lit_int = literal.satVariable.positive_int
    other_int = literal.satVariable.negative_int
  else:
    lit_int = literal.satVariable.negative_int
    other_int = literal.satVariable.positive_int
  return lit_int, other_int, is_positive

def assign_true(
  literal: SATLiteral,
  itc: List[List[SATClause]], # int to clauses
  assigned_literals=[]
):
  if literal.satVariable.truth_value is not None:
    raise RuntimeError(f"`{str(literal)}` was supposed to be unassigned!")
  assigned_literals.append(literal)
  lit_int, other_int, is_positive = get_literal_int(literal)
  literal.satVariable.truth_value = is_positive

  positive_clauses = itc[lit_int]
  for clause in positive_clauses:
    clause.n_satisfied += 1
    if clause.n_satisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{str(clause)}`: n_satisfied > len(clause)")
  
  negative_clauses = itc[other_int]
  result = UnitPropagationResult.SUCCESS
  for clause in negative_clauses:
    clause.n_unsatisfied += 1
    if clause.n_unsatisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{str(clause)}`: n_unsatisfied > len(clause)")
    if clause.n_unsatisfied == len(clause):
      result = UnitPropagationResult.CONFLICT
  
  return result

def unassign(
  literal: SATLiteral,
  itc: List[List[SATClause]], # int to clauses
):
  if literal.satVariable.truth_value is None:
    raise RuntimeError(f"`{str(literal)}` was supposed to be assigned!")
  lit_int, other_int, is_positive = get_literal_int(literal)

  literal.satVariable.truth_value = None
  
  positive_clauses = itc[lit_int]
  for clause in positive_clauses:
    clause.n_satisfied -= 1
    if clause.n_satisfied < 0:
      raise RuntimeError(f"UNASSIGN on `{str(clause)}`: n_satisfied < 0")

  negative_clauses = itc[other_int]
  for clause in negative_clauses:
    clause.n_unsatisfied -= 1
    if clause.n_unsatisfied < 0:
      raise RuntimeError(f"UNASSIGN on `{str(clause)}`: n_unsatisfied < 0 (all clauses: {itc[other_int]}) (literal: {literal})")

def unassign_multiple(
  ls: List[SATLiteral],
  itc: List[List[SATClause]]
):
  for l in ls:
    unassign(l, itc)
