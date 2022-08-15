from logzero import logger
from satsolver.utils.enums import UnitPropagationResult, SATSolverResult
from satsolver.utils.representation import debug_str, debug_str_multi
from satsolver.utils.stats import SATSolverStats

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
    self.health_check       = None

  def __debug_print_unsatisfied(self, c):
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

  def __dpll(
    self,
    dec_var_int,
    itv, # int to variable
    itc, # int to clause
    assignment,
    c, # clauses
    stats: SATSolverStats,
    n_variables,
    debug,
    n_assigned_variables
  ):
    #self.__debug_print_unsatisfied(c)
    cs = c # cs == clauses to search
    if dec_var_int is not None:
      cs = itc[dec_var_int]
    unitPropResult, assigned_literals = self.unit_propagation(itv, itc, assignment, cs, stats)

    if unitPropResult == UnitPropagationResult.CONFLICT:
      return SATSolverResult.UNSAT, assigned_literals

    # end condition -> each variable is assigned and there is no conflict
    n_assigned_variables += len(assigned_literals)
    if debug:
      logger.debug(f"UP: {debug_str_multi(assigned_literals, itv)}")
    if n_assigned_variables == n_variables:
      logger.debug(f"RESULT: {debug_str_multi([i + i for i, v in enumerate(assignment) if v == 1], itv)}")
      return SATSolverResult.SAT, None

    var_int = self.dec_var_selection(assignment)

    # positive literal: var_int << 1
    satResultPos = self._dpll(var_int << 1, itv, itc, assignment, c, stats, n_variables, debug, n_assigned_variables)
    if satResultPos == SATSolverResult.SAT:
      return satResultPos, None

    # negative literal: var_int << 1 | 1
    satResultNeg = self._dpll(var_int << 1 | 1, itv, itc, assignment, c, stats, n_variables, debug, n_assigned_variables)
    if satResultNeg == SATSolverResult.SAT:
      return satResultNeg, None

    return SATSolverResult.UNSAT, assigned_literals

  def _dpll(
    self,
    dec_lit_int,
    itv, # int to variable
    itc, # int to clause
    assignment,
    c, # clauses
    stats: SATSolverStats,
    n_variables,
    debug,
    n_assigned_variables
  ):
    """
    Assigns true to literal which has index `dec_lit_int` in table `itl` (int to literal). Calls `__dpll`.
    Also unassigns in case of `UNSAT` (e.g. removes the need for unassignments in all cases where `__dpll`
    can return `UNSAT`)
    """
    other_int = None
    if dec_lit_int is not None:
      other_int = dec_lit_int ^ 1
      self.assign_true(dec_lit_int, itv, assignment, itc)
      if debug:
        logger.debug(f"DEC: {debug_str(dec_lit_int, itv)}")
      stats.decVars += 1
      n_assigned_variables += 1

    result, assigned_literals = self.__dpll(other_int, itv, itc, assignment, c, stats, n_variables, debug, n_assigned_variables)
    if result == SATSolverResult.UNSAT:
      if len(assigned_literals) != 0 and debug:
        logger.debug(f"DPLL: Conflict: {debug_str_multi(assigned_literals, itv)}")
      self.unassign_multiple(assigned_literals, assignment, itc, itv)
      if dec_lit_int is not None:
        if debug:
          logger.debug(f"UNDEC: {debug_str(dec_lit_int, itv)}")
        self.unassign(dec_lit_int, assignment, itc, itv)

    return result

  def dpll(self,ast_tree_root, debug):
    assignment, itv, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._dpll(None, itv, itc, assignment, c, stats, n_variables, debug, n_assigned_variables=0)

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
