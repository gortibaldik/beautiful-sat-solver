from logzero import logger
from satsolver.utils.enums import UnitPropagationResult, SATSolverResult
from satsolver.utils.representation import debug_str, debug_str_multi
from ..utils.stats import SATSolverStats
from satsolver.watched_literals.representation import SATClause
from typing import List

class DPLLIter:
  """Implementation of DPLL that uses cycle instead of recursion"""
  def __init__(
    self,
    prepare_structures,
    unit_propagation,
    dec_var_selection,
    assign_true,
    unassign,
    unassign_multiple
  ):
    self.prepare_structures = prepare_structures
    self.unit_propagation   = unit_propagation
    self.dec_var_selection  = dec_var_selection
    self.assign_true        = assign_true
    self.unassign           = unassign
    self.unassign_multiple  = unassign_multiple
    self.health_check       = None

  def __debug_print_unsatisfied(self, c: List[SATClause]):
    s = ""
    for clause, _ in c:
      is_satisfied = False
      for child in clause.children:
        if child.is_satisfied():
          is_satisfied = True
          break
      if not is_satisfied:
        if len(s) == 0:
          s = str(clause)
        else:
          s += f"; {clause}"

    logger.debug(s)
  
  def _dpll(
    self,
    itv,
    itc,
    assignment,
    c,
    stats: SATSolverStats,
    n_variables,
    debug
  ):
    stack_dec_var_int = [None] * n_variables
    stack_assigned_literals = [None] * n_variables
    stack_decisions = [0] * n_variables
    n_assigned_variables = 0
    ix = 0

    while True:
      # what has already been tried at level ix
      decision = stack_decisions[ix]

      if ix == 0:
        # UP at the 0th level has already been
        # done the clause is UNSAT
        if decision == 1:
          return SATSolverResult.UNSAT
        else:
          stack_decisions[ix] = 1
          cs = c

      else:
        dec_var_int = stack_dec_var_int[ix]
        if decision == 0:
          dec_lit_int = dec_var_int + dec_var_int
          stack_decisions[ix] += 1
          n_assigned_variables += 1
          stats.decVars += 1
        elif decision == 1:
          # unassign last decision literal
          dec_lit_int = dec_var_int + dec_var_int
          if debug: logger.debug(f"UNDEC: {debug_str(dec_lit_int, itv)}")
          self.unassign(dec_lit_int, assignment, itc, itv)
          dec_lit_int += 1
          stack_decisions[ix] += 1
          stats.decVars += 1
        else:
          # unassign last decision literal
          dec_lit_int = dec_var_int + dec_var_int + 1
          if debug: logger.debug(f"UNDEC: {debug_str(dec_lit_int, itv)}")
          self.unassign(dec_lit_int, assignment, itc, itv)

          assigned_literals = stack_assigned_literals[ix]
          if debug: logger.debug(f"DPLL: Conflict: {debug_str_multi(assigned_literals, itv)}")
          self.unassign_multiple(assigned_literals, assignment, itc, itv)
          
          # restore structures
          stack_decisions[ix] = 0
          ix -= 1
          n_assigned_variables -= (1 + len(assigned_literals))
          continue
        
        if debug: logger.debug(f"DEC: {debug_str(dec_lit_int, itv)}")
        self.assign_true(dec_lit_int, itv, assignment, itc)
        cs = itc[dec_lit_int ^ 1]

      unitPropResult, assigned_literals = self.unit_propagation(itv, itc, assignment, cs, stats)
      if unitPropResult == UnitPropagationResult.CONFLICT:
        continue

      if debug: logger.debug(f"UP: {debug_str_multi(assigned_literals, itv)}")
      
      ix += 1
      n_assigned_variables += len(assigned_literals)
      if n_assigned_variables == n_variables:
        return SATSolverResult.SAT
      stack_assigned_literals[ix] = assigned_literals
      stack_dec_var_int[ix] = self.dec_var_selection(assignment)

  def dpll(self,ast_tree_root, debug):
    assignment, itv, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._dpll(itv, itc, assignment, c, stats, n_variables, debug)

    # health check
    if result == SATSolverResult.UNSAT and self.health_check is not None:
      self.health_check(c)

    # construct model
    model = None
    if result == SATSolverResult.SAT:
      model = {}
      for var_name, ipos in vti.items():
        model[var_name] = assignment[ipos]

    return result.value, model, stats
