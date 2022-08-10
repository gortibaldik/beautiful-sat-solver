from logzero import logger
from satsolver.utils.enums import UnitPropagationResult, SATSolverResult
from typing import List

from satsolver.utils.structures_preparation import get_literal_int
from satsolver.watched_literals.representation import SATClause

class DPLLCycle:
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
    itc,
    itl,
    c,
    stats,
    n_variables
  ):
    n_assigned_variables = 0

    unitPropResult, assigned_literals = self.unit_propagation(itc, c, c, stats)
    if unitPropResult == UnitPropagationResult.CONFLICT:
      return SATSolverResult.UNSAT
    
    n_assigned_variables = len(assigned_literals)
    logger.debug(f"UP: {assigned_literals}")
    pos_int, neg_int = self.dec_var_selection(itl)
    stack_dec_var_int = [None, neg_int, pos_int]
    stack_assigned_literals = []
    stack_assigned_literals_up = []


    while True:
      dec_var_int = stack_dec_var_int.pop()
      if dec_var_int is None:
        # we are back at the top level: return UNSAT
        if n_assigned_variables == 0:
          return SATSolverResult.UNSAT
        
        # not at the top level:
        # we need to backtrack to upper-part, at first
        # unassign literals derived in unit propagation
        # and unassign the decision literal
        lit_to_unassign = stack_assigned_literals.pop()
        ups_to_unassign = stack_assigned_literals_up.pop()
        if len(ups_to_unassign) != 0:
          logger.debug(f"DPLL: Conflict: {ups_to_unassign}")
        self.unassign_multiple(ups_to_unassign, itc)
        logger.debug(f"UNDEC: {literal}")
        self.unassign(lit_to_unassign, itc)
        n_assigned_variables -= (1 + len(ups_to_unassign))
        continue

      literal = itl[dec_var_int]
      lit_int, other_int = get_literal_int(literal)
      self.assign_true(literal, itc)
      logger.debug(f"DEC: {literal}")
      stats.decVars += 1
      cs = itc[other_int]

      unitPropResult, assigned_literals = self.unit_propagation(itc, cs, c, stats)

      if unitPropResult == UnitPropagationResult.CONFLICT:
        self.unassign(literal, itc)
        logger.debug(f"UNDEC: {literal}")
        continue

      stack_assigned_literals.append(literal)
      stack_assigned_literals_up.append(assigned_literals)
      n_assigned_variables += 1 + len(assigned_literals)

      logger.debug(f"UP: {assigned_literals}")
      if n_assigned_variables == n_variables:
        return SATSolverResult.SAT
      
      try:
        pos_int, neg_int = self.dec_var_selection(itl)
      except:
        logger.warning(f"Exception in dec_var_selection, n_assigned_variables: {n_assigned_variables}, n_variables: {n_variables}")
      stack_dec_var_int.append(None)
      stack_dec_var_int.append(neg_int)
      stack_dec_var_int.append(pos_int)

  def dpll(self,ast_tree_root, debug):
    itl, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._dpll(itc, itl, c, stats, n_variables)

    # health check
    if result == SATSolverResult.UNSAT and self.health_check is not None:
      self.health_check(c)

    # construct model
    model = None
    if result == SATSolverResult.SAT:
      model = {}
      for var_name, (ipos, ineg) in vti.items():
        model[var_name] = itl[ipos].satVariable.truth_value

    return result.value, model, stats
