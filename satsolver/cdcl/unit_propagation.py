from logzero import logger
from satsolver.cdcl.representation import CDCLData
from satsolver.utils.enums import UnitPropagationResult
from satsolver.utils.representation import debug_str_multi
from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.assignment import assign_true
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

def find_unit_clauses(data:CDCLData):
  unit_clauses: List[Tuple[SATClause, int]] = []
  assignment = data.assignment
  for entry in data.cs:
    clause, watched_index = entry
    children = clause.children
    watched = clause.watched
    data.stats.unitPropCheckedClauses += 1

    if watched_index == -1:
      # only in the initial unit propagation we traverse
      # a list where watched_index == -1, therefore there
      # we only need to check for real unit clauses (only
      # one literal clauses)
      if watched[1] is None:
        lit_int = clause[0]
        if assignment[lit_int >> 1] is None:
          unit_clauses.append((clause, lit_int))
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

  return UnitPropagationResult.NOTHING_FOUND, unit_clauses

def _unit_propagation(
  data: CDCLData,
  first_index = -2
):
  assigned_literals = []
  list_of_cs = [data.cs]
  ix = first_index
  while len(list_of_cs) > 0:
    data.cs = list_of_cs.pop()
    # additional info is a list of unit clauses if result != conflict
    # additional info is a clause where the conflict was found
    result, additional_info = find_unit_clauses(data)

    if result == UnitPropagationResult.CONFLICT:
      return additional_info, assigned_literals

    for clause, lit_int in additional_info:
      var_int = lit_int >> 1
      a_l = data.assignment[var_int]

      # clause is unsatisfied
      if a_l == (lit_int & 1):
        return clause, assigned_literals

      # is satisfied (not unsatisfied and not None)
      if a_l is not None:
        continue

      data.antecedents[var_int] = clause
      data.dec_lvls_of_vars[var_int] = (data.current_dec_lvl, ix)
      ix -= 1
      assign_true(
        lit_int,
        data.itv,
        data.assignment,
        data.itc,
        assigned_literals
      )
      data.stats.unitProps += 1
      list_of_cs.append(data.itc[lit_int ^ 1])

  return None, assigned_literals

def unit_propagation(data: CDCLData, first_index=-2):
  result, assigned_literals = _unit_propagation(data, first_index)
  data.assigned_literals[data.current_dec_lvl] = assigned_literals
  data.n_assigned_variables += len(assigned_literals)
  return result