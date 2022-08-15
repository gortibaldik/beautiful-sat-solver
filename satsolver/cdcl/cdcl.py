from logzero import logger
from satsolver.utils.enums import SATSolverResult, UnitPropagationResult
from satsolver.utils.representation import debug_str, debug_str_multi
from ..utils.stats import SATSolverStats


class CDCL:
  def __init__(
    self,
    prepare_structures,
    unit_propagation,
    dec_var_selection,
    assign_true,
    unassign,
    unassign_multiple,
    conflict_analysis
  ):
    self.prepare_structures = prepare_structures
    self.unit_propagation   = unit_propagation
    self.dec_var_selection  = dec_var_selection
    self.assign_true        = assign_true
    self.unassign           = unassign
    self.unassign_multiple  = unassign_multiple
    self.conflict_analysis  = conflict_analysis
    self.health_check       = None

  def _cdcl(
    self,
    itv,
    itc,
    assignment,
    c,
    stats: SATSolverStats,
    n_variables,
    debug
  ):
    decisions = [0] * n_variables
    assigned_literals = [None] * n_variables
    dec_vars = [None] * n_variables
    antecedents = [None] * n_variables
    dec_lvls_of_vars = [-1] * n_variables
    current_dec_lvl = 0
    cs = c

    unitPropResult, al = self.unit_propagation(
      itv,
      itc,
      assignment,
      antecedents,
      dec_lvls_of_vars,
      current_dec_lvl,
      c,
      stats
    )
    if unitPropResult == UnitPropagationResult.CONFLICT:
      return SATSolverResult.UNSAT
    if debug: logger.debug(f"UP: {debug_str_multi(al, itv)}")
    n_assigned_variables = len(al)

    while True:
      decision = decisions[current_dec_lvl]
      decisions[current_dec_lvl] += 1
      if decision == 0:
        var_int = self.dec_var_selection(assignment)
        dec_vars[current_dec_lvl] = var_int
        lit_int = var_int + var_int
        n_assigned_variables += 1
      elif decision == 1:
        var_int = dec_vars[current_dec_lvl]
        lit_int = var_int + var_int
        if debug: logger.debug(f"UNDEC: {debug_str(lit_int, itv)}")
        self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
        lit_int += 1
      else:
        var_int = dec_vars[current_dec_lvl]
        decisions[current_dec_lvl] = 0
        lit_int = var_int + var_int + 1
        if debug: logger.debug(f"UNDEC: {debug_str(lit_int, itv)}")
        self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)

        current_dec_lvl -= 1
        if current_dec_lvl < 0:
          break
        if debug and len(assigned_literals[current_dec_lvl]) > 0: logger.debug(f"DPLL: Conflict: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")
        self.unassign_multiple(assigned_literals[current_dec_lvl], assignment, dec_lvls_of_vars, itc, itv)
        n_assigned_variables -= (1+ len(assigned_literals[current_dec_lvl]))
        continue

      if debug: logger.debug(f"DEC: {debug_str(lit_int, itv)}")
      stats.decVars += 1
      self.assign_true(lit_int, itv, assignment, itc)
      cs = itc[lit_int ^ 1]
      conflict_clause, assigned_literals[current_dec_lvl] = self.unit_propagation(
        itv,
        itc,
        assignment,
        antecedents,
        dec_lvls_of_vars,
        current_dec_lvl,
        cs,
        stats
      )
      if conflict_clause is not None:
        self.unassign_multiple(assigned_literals[current_dec_lvl], assignment, dec_lvls_of_vars, itc, itv)
        continue
      n_assigned_variables += len(assigned_literals[current_dec_lvl])

      if debug: logger.debug(f"UP: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")

      if n_assigned_variables == n_variables:
        logger.debug(f"RESULT: {debug_str_multi([i + i for i, v in enumerate(assignment) if v == 1], itv)}")
        return SATSolverResult.SAT
      current_dec_lvl += 1
    return SATSolverResult.UNSAT
  
  def cdcl(self,ast_tree_root, debug):
    assignment, itv, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._cdcl(itv, itc, assignment, c, stats, n_variables, debug)

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