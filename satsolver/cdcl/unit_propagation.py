from logzero import logger
from satsolver.cdcl.assignment import unassign_multiple
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.assignment import assign_true
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
    children = clause.children
    watched = clause.watched
    stats.unitPropCheckedClauses += 1

    if watched_index == -1:
      # only in the initial unit propagation we traverse
      # a list where watched_index == -1, therefore there
      # we only need to check for real unit clauses (only
      # one literal clauses)
      if watched[1] is None:
        unit_clauses.append((clause, 0))
        continue
      continue
      
    # satisfied clause
    lit_w = children[watched[watched_index]]
    a_w = assignment[lit_w >> 1]
    if a_w == ((lit_w & 1) ^ 1):
      continue

    lit_o = children[watched[watched_index ^ 1]]
    a_o = assignment[lit_o >> 1]
    if a_o == ((lit_o & 1) ^ 1):
      continue

    # assignment => watched literal in clause becomes False
    # => new literal is found
    # => if it is unsatisfied then it means that the clause is either
    # unit of conflict
    if a_w is not None:
      if a_o is None:
        unit_clauses.append((clause, lit_o))
      else:
        return UnitPropagationResult.CONFLICT, clause

  if len(unit_clauses) > 0:
    return UnitPropagationResult.UNIT_FOUND, unit_clauses

  return UnitPropagationResult.NOTHING_FOUND, unit_clauses

def unit_propagation(
  itv, # int to variables
  itc, # int to clauses
  assignment,
  antecedents,
  dec_lvls_of_vars,
  current_dec_lvl,
  cs,  # clauses to search
  stats: SATSolverStats
):
  assigned_literals = []
  list_of_cs = [cs]
  while len(list_of_cs) > 0:
    cs = list_of_cs.pop()
    # additional info is a list of unit clauses if result != conflict
    # additional info is a clause where the conflict was found
    result, additional_info = find_unit_clauses(itv, cs, assignment, stats)

    if result == UnitPropagationResult.CONFLICT:
      return additional_info, assigned_literals

    # implicitly result == (UnitPropagationResult.NOTHING_FOUND or UnitPropagationResult.UNIT_FOUND)
    for clause, lit_int in additional_info:
      var_int = lit_int >> 1
      a_l = assignment[var_int]

      # clause is unsatisfied
      if a_l == (lit_int & 1):
        return clause, assigned_literals

      # is satisfied (not unsatisfied and not None)
      if a_l is not None:
        continue
      antecedents[var_int] = clause
      dec_lvls_of_vars[var_int] = current_dec_lvl

      assign_true(
        lit_int,
        itv,
        assignment,
        itc,
        assigned_literals
      )
      stats.unitProps += 1
      list_of_cs.append(itc[lit_int ^ 1])

  return None, assigned_literals
