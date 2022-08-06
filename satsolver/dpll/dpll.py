from logzero import logger
from satsolver.utils.enums import DecisionVariableResult, UnitPropagationResult, SATSolverResult
from satsolver.utils.representation import SATLiteral
from satsolver.utils.stats import SATSolverStats
from typing import List

from satsolver.utils.structures_preparation import get_literal_int

class DPLL:
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

  def __dpll(
    self,
    dec_var_int,
    itc, # int to clause
    itl: List[SATLiteral], # int to literal
    c, # clauses
    stats: SATSolverStats,
    n_variables,
    n_assigned_variables
  ):
    cs = c # cs == clauses to search
    if dec_var_int is not None:
      cs = itc[dec_var_int]
    unitPropResult, assigned_literals = self.unit_propagation(itc, cs, c, stats)

    if unitPropResult == UnitPropagationResult.CONFLICT:
      return SATSolverResult.UNSAT, assigned_literals

    # end condition -> each variable is assigned and there is no conflict
    n_assigned_variables += len(assigned_literals)
    if n_assigned_variables == n_variables:
      logger.debug(f"UP: {assigned_literals}")
      return SATSolverResult.SAT, None

    logger.debug(f"UP: {assigned_literals}")

    pos_int, neg_int = self.dec_var_selection(itl)

    satResultPos = self._dpll(pos_int, itc, itl, c, stats, n_variables, n_assigned_variables)
    if satResultPos == SATSolverResult.SAT:
      return satResultPos, None

    satResultNeg = self._dpll(neg_int, itc, itl, c, stats, n_variables, n_assigned_variables)
    if satResultNeg == SATSolverResult.SAT:
      return satResultNeg, None

    return SATSolverResult.UNSAT, assigned_literals

  def _dpll(
    self,
    dec_var_int,
    itc, # int to clause
    itl: List[SATLiteral], # int to literal
    c, # clauses
    stats: SATSolverStats,
    n_variables,
    n_assigned_variables
  ):
    """
    Assigns true to literal which has index `dec_var_int` in table `itl` (int to literal). Calls `__dpll`.
    Also unassigns in case of `UNSAT` (e.g. removes the need for unassignments in all cases where `__dpll`
    can return `UNSAT`)
    """
    other_int, literal = None, None
    if dec_var_int is not None:
      literal = itl[dec_var_int]
      lit_int, other_int = get_literal_int(literal)
      self.assign_true(literal, itc)
      stats.decVars += 1
      n_assigned_variables += 1

    result, assigned_literals = self.__dpll(other_int, itc, itl, c, stats, n_variables, n_assigned_variables)
    if result == SATSolverResult.UNSAT:
      if len(assigned_literals) != 0:
        logger.debug(f"DPLL: Conflict: {assigned_literals}")
      self.unassign_multiple(assigned_literals, itc)
      if literal is not None:
        self.unassign(literal, itc)

    return result

  def dpll(self,ast_tree_root):
    itl, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._dpll(None, itc, itl, c, stats, n_variables, n_assigned_variables=0)

    # health check
    if result == SATSolverResult.UNSAT:
      for clause in c:
        if clause.n_satisfied != 0 or clause.n_unsatisfied != 0:
          raise RuntimeError(f"SATSolverResult == UNSAT while there are still assignments pending!")

    # construct model
    model = None
    if result == SATSolverResult.SAT:
      model = {}
      for var_name, (ipos, ineg) in vti.items():
        model[var_name] = itl[ipos].satVariable.truth_value

    return result.value, model, stats
