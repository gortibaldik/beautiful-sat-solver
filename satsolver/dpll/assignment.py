from satsolver.dpll.representation import SATClause
from satsolver.utils.representation import SATLiteral
from satsolver.utils.structures_preparation import get_literal_int
from typing import List

def assign_true(
  literal: SATLiteral,
  itc: List[List[SATClause]], # int to clauses
  assigned_literals=[]
):
  if literal.is_assigned():
    raise RuntimeError(f"`{str(literal)}` was supposed to be unassigned!")
  assigned_literals.append(literal)
  lit_int, other_int = get_literal_int(literal)
  literal.satisfy()

  positive_clauses = itc[lit_int]
  for clause in positive_clauses:
    clause.n_satisfied += 1
    if clause.n_satisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{str(clause)}`: n_satisfied > len(clause)")
  
  negative_clauses = itc[other_int]
  for clause in negative_clauses:
    clause.n_unsatisfied += 1
    if clause.n_unsatisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{str(clause)}`: n_unsatisfied > len(clause)")

def unassign(
  literal: SATLiteral,
  itc: List[List[SATClause]], # int to clauses
):
  if not literal.is_assigned():
    raise RuntimeError(f"`{str(literal)}` was supposed to be assigned!")
  lit_int, other_int = get_literal_int(literal)

  literal.unassign()
  
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
