from satsolver.dpll.representation import SATClause
from satsolver.utils.representation import debug_str, lit_is_assigned, lit_is_none, satisfy_lit, unassign_lit
from typing import List

def assign_true(
  lit_int: int, # literal
  itv,  # int to variable
  assignment,
  itc: List[List[SATClause]], # int to clauses
  assigned_literals=[]
):
  if lit_is_assigned(lit_int, assignment):
    raise RuntimeError(f"`{debug_str(lit_int, itv)}` was supposed to be unassigned!")
  assigned_literals.append(lit_int)

  satisfy_lit(lit_int, assignment)

  positive_clauses = itc[lit_int]
  for clause in positive_clauses:
    clause.n_satisfied += 1
    if clause.n_satisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{clause.debug_str}`: n_satisfied > len(clause)")
  
  negative_clauses = itc[lit_int ^ 1]
  for clause in negative_clauses:
    clause.n_unsatisfied += 1
    if clause.n_unsatisfied > len(clause):
      raise RuntimeError(f"ASSIGN on `{clause.debug_str}`: n_unsatisfied > len(clause)")

def unassign(
  lit_int: int, # literal
  assignment,
  itc: List[List[SATClause]], # int to clauses
  itv: List[str] # int to var
):
  if lit_is_none(lit_int, assignment):
    raise RuntimeError(f"`{debug_str(lit_int, itv)}` was supposed to be assigned!")

  unassign_lit(lit_int, assignment)
  
  positive_clauses = itc[lit_int]
  for clause in positive_clauses:
    clause.n_satisfied -= 1
    if clause.n_satisfied < 0:
      raise RuntimeError(f"UNASSIGN on `{clause.debug_str}`: n_satisfied < 0")

  negative_clauses = itc[lit_int ^ 1]
  for clause in negative_clauses:
    clause.n_unsatisfied -= 1
    if clause.n_unsatisfied < 0:
      raise RuntimeError(f"UNASSIGN on `{clause.debug_str}`: n_unsatisfied < 0 (all clauses: {itc[lit_int ^ 1]}) (literal: {debug_str(lit_int, itv)})")

def unassign_multiple(
  ls: List[int], # literals
  assignment,
  itc: List[List[SATClause]], # int to clauses
  itv: List[str] # int to var
):
  for l in ls:
    unassign(l, assignment, itc, itv)
