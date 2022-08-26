from typing import List, Protocol, Tuple
from logzero import logger

from satsolver.cdcl.representation import CDCLConfig, CDCLData, SATClause
from satsolver.utils.enums import SATSolverResult, UnitPropagationResult
from satsolver.utils.representation import debug_str, debug_str_multi
from ..utils.stats import SATSolverStats
class UnassignMultiple(Protocol):
  def __call__(
    self,
    ls: List[int],
    assignment: List[int],
    dec_lvls_of_vars: List[Tuple[int, int]],
    itc: List[List[SATClause]],
    itv: List[str]
  ): ...

class Unassign(Protocol):
  def __call__(
    self,
    lit_int: int,
    assignment: List[int],
    dec_lvls_of_vars,
    itc: List[List[SATClause]], # int to clauses
    itv: List[str]
  ): ...



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
    self.unassign: Unassign                   = unassign
    self.unassign_multiple: UnassignMultiple  = unassign_multiple
    self.conflict_analysis  = conflict_analysis
    self.health_check       = None
  
  def _clause_str(self, clause, data):
    s = []
    for lit_int in clause.children:
      _s = debug_str(lit_int, data.itv) + "_@_" + str(data.dec_lvls_of_vars[lit_int >> 1][0])
      _s += "_"
      var_int = lit_int >> 1
      if data.dec_lvls_of_vars[var_int][0] == data.current_dec_lvl:
        _s += "[*]"
      elif data.assignment[var_int] is None:
        _s += "[?]"
      elif data.assignment[var_int] == lit_int & 1:
        _s += "[F]"
      else:
        _s += "[T]"
      s.append(_s)
    
    return s

  def _add_to_structures(
    self,
    assertive_clause,
    learned_clauses,
    itc
  ):
    learned_clauses.append(assertive_clause)
    if len(assertive_clause) > 1:
      watched = assertive_clause.watched
      lit_1 = assertive_clause.children[watched[0]]
      lit_2 = assertive_clause.children[watched[1]]
      itc[lit_1].append((assertive_clause, 0))
      itc[lit_2].append((assertive_clause, 1))
    else:
      lit_1 = assertive_clause[0]
      itc[lit_1].append((assertive_clause, -1))
    return lit_1
  
  def _deep_backtrack(self, data: CDCLData, debug):
    # decision cheat sheet
    # decision == 0 -> dec_var_selection should be done in _set_decision_lit
    # decision == 1 == 001 -> False literal should be selected in _set_decision_lit as the first option
    # decision == 2 == 010 -> True literal should be selected in _set_decision_lit as the first option
    #
    # decision == 4 == 100 -> True literal should be selected in _set_decision_lit as the second option
    # decision == 5 == 101 -> False literal should be selected in _set_decision_lit as the second option
    #
    # when only backjumping (e.g. assertion lvl is 4, so we need to backjump at lvl 4, but not undo
    # unit propagation or dec var selection, then decision > 5 (we add 6 to decision, so its value
    # varies from 7 to 11) and then modulo it by 6 to get it back to where it was)
    new_dec_lvl = data.current_dec_lvl
    n_removed_literals = 0
    
    while data.decisions[new_dec_lvl] > 3:
      data.decisions[new_dec_lvl] = 0
      var_int = data.dec_vars[new_dec_lvl]
      lit_int = var_int + var_int + 1

      if debug: logger.debug(f"{data.current_dec_lvl}: UNDEC CL: {debug_str(lit_int, data.itv)}")
      self.unassign(lit_int, data.assignment, data.dec_lvls_of_vars, data.itc, data.itv)
      n_removed_literals += 1

      # remove unit propagation
      new_dec_lvl -= 1
      if debug:
        logger.debug(f"{new_dec_lvl}: CL UP UNDO: {debug_str_multi(data.assigned_literals[new_dec_lvl], data.itv)}")
      self.unassign_multiple(
        data.assigned_literals[new_dec_lvl],
        data.assignment,
        data.dec_lvls_of_vars,
        data.itc,
        data.itv
      )
      n_removed_literals += len(data.assigned_literals[new_dec_lvl])
    
    # we either backtracked to level 0,
    # then the formula is UNSAT
    if new_dec_lvl == 0:

      # we return -1 as the new decision lvl
      # because 0 is a valid value, when backjumping
      # with learning is done
      return n_removed_literals, -1
    
    # else we backtracked to some previous literal
    # decision, so now we need to invert that decision
    var_int = data.dec_vars[new_dec_lvl]
    lit_int = var_int + var_int + (data.decisions[new_dec_lvl] & 1)
    self.unassign(lit_int, data.assignment, data.dec_lvls_of_vars, data.itc, data.itv)
    data.decisions[new_dec_lvl] += 3
    n_removed_literals += 1
    return n_removed_literals, new_dec_lvl

  def _shallow_backtrack(self, data, debug):
    # decision cheat sheet
    # decision == 0 -> dec_var_selection should be done in _set_decision_lit
    # decision == 1 == 001 -> False literal should be selected in _set_decision_lit as the first option
    # decision == 2 == 010 -> True literal should be selected in _set_decision_lit as the first option
    #
    # decision == 4 == 100 -> True literal should be selected in _set_decision_lit as the second option
    # decision == 5 == 101 -> False literal should be selected in _set_decision_lit as the second option
    #
    # when only backjumping (e.g. assertion lvl is 4, so we need to backjump at lvl 4, but not undo
    # unit propagation or dec var selection, then decision > 5 (we add 6 to decision, so its value
    # varies from 7 to 11) and then modulo it by 6 to get it back to where it was)
    decision = data.decisions[data.current_dec_lvl]
    var_int = data.dec_vars[data.current_dec_lvl]
    lit_int = var_int + var_int + (decision & 1)
    new_dec_lvl = data.current_dec_lvl
    n_removed_literals = 0


    # if we took some literal
    # then it still remains to check the
    # other one
    #
    # hence we need to remove unit propagation
    # and retry the second branch 
    if decision < 3:
      if debug: logger.debug(f"{data.current_dec_lvl}: UNDEC CL: {debug_str(lit_int, data.itv)}")
      self.unassign(lit_int, data.assignment, data.dec_lvls_of_vars, data.itc, data.itv)
      n_removed_literals += 1

      # tell the algorithm to take another branch next time
      # on this level
      data.decisions[new_dec_lvl] += 3


      # unit propagation was done at the previous level
      new_dec_lvl -= 1

      # assertive clause is unit at new_dec_lvl so the unit propagation
      # needs to be redone, however there is no need to repeat the decision
      # and original unit propagation at new_dec_lvl
      data.decisions[new_dec_lvl] += 6
      return n_removed_literals, new_dec_lvl
    else:
      return self._deep_backtrack(data, debug)

  def _backjump(self, data: CDCLData, assertion_lvl, debug):
    # decision cheat sheet
    # when only backjumping (e.g. assertion lvl is 4, so we need to backjump at lvl 4, but not undo
    # unit propagation or dec var selection, then decision > 5 (we add 6 to decision, so its value
    # varies from 7 to 11) and then modulo it by 6 to get it back to where it was)
    new_dec_lvl = data.current_dec_lvl
    n_removed_literals = 0

    # example
    # U3 -> conflict -> assertion_lvl = 0
    # U(N-1) <- D(N) means unassignment of unit_propped vars
    # D(N) <- U(N) means unassignment of dec_var
    # 
    # U3 <- conflict done in _backtrack function
    # U2 <- D3 <- U3 done in iteration 1
    # U1 <- D2 <- U2 done in iteration 2
    # D1 <- U1 done manually after the loop
    #
    # it is not needed to remove unit_propped vars
    # at level 0, we just need to start unit propagation
    # with some false literal in assertive clause
    # 
    while assertion_lvl < new_dec_lvl - 1:
      var_int = data.dec_vars[new_dec_lvl]
      lit_int = var_int + var_int + (data.decisions[new_dec_lvl] & 1)

      # backtrack from that level
      if debug: logger.debug(f"{new_dec_lvl}: UNDEC CL: {debug_str(lit_int, data.itv)}")
      self.unassign(lit_int, data.assignment, data.dec_lvls_of_vars, data.itc, data.itv)
      data.decisions[new_dec_lvl] = 0
      new_dec_lvl -= 1
      n_removed_literals += 1

      # remove unit propagation
      if debug:
        logger.debug(f"{new_dec_lvl}: CL UP UNDO: {debug_str_multi(data.assigned_literals[new_dec_lvl], data.itv)}")
      self.unassign_multiple(
        data.assigned_literals[new_dec_lvl],
        data.assignment,
        data.dec_lvls_of_vars,
        data.itc,
        data.itv
      )
      n_removed_literals += len(data.assigned_literals[new_dec_lvl])

    var_int = data.dec_vars[new_dec_lvl]
    lit_int = var_int + var_int + (data.decisions[new_dec_lvl] & 1)
    if debug: logger.debug(f"{new_dec_lvl}: UNDEC CL: {debug_str(lit_int, data.itv)}")
    self.unassign(lit_int, data.assignment, data.dec_lvls_of_vars, data.itc, data.itv)
    n_removed_literals += 1

    new_dec_lvl -= 1
    data.decisions[new_dec_lvl] += 6

    return n_removed_literals, new_dec_lvl


  def _backtrack(self, conflict_clause, data: CDCLData, debug):
    # if backtrack happens only for one step, then data.decisions[lvl]
    # is incremented by 6, so that the literal selection is remembered
    #
    # when up finds conflict, we need to set the value to 0
    data.decisions[data.current_dec_lvl + 1] = 0

    data.stats.conflicts += 1
    if debug:
      logger.debug(f"{data.current_dec_lvl}: CONFLICT CLAUSE: {self._clause_str(conflict_clause, data)}")
    if data.current_dec_lvl == 0:
      data.current_dec_lvl = -1
      return 0, 0
    assertive_clause, assertion_lvl = self.conflict_analysis(conflict_clause, data)
    if debug:
      logger.debug(f"{data.current_dec_lvl}: ASSERTIVE CLAUSE: {self._clause_str(assertive_clause, data)}" + \
        f"LBD: {assertive_clause.lbd}"+ f"; AL: {assertion_lvl}")
      #logger.debug(f"{current_dec_lvl}: CL UP UNDO: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")
    self.unassign_multiple(
      data.assigned_literals[data.current_dec_lvl],
      data.assignment,
      data.dec_lvls_of_vars,
      data.itc,
      data.itv
    )
    remove_from_assigned_variables = len(data.assigned_literals[data.current_dec_lvl])
    next_unit_prop_lit_int = self._add_to_structures(assertive_clause, data.learned_clauses, data.itc)

    if assertion_lvl == data.current_dec_lvl - 1:
      nrl, new_dec_lvl = self._shallow_backtrack(data, debug)
      remove_from_assigned_variables += nrl
    else:
      nrl, new_dec_lvl = self._backjump(data, assertion_lvl, debug)
      remove_from_assigned_variables += nrl

    data.current_dec_lvl = new_dec_lvl
    data.n_assigned_variables -= remove_from_assigned_variables
    return next_unit_prop_lit_int

  def _clause_deletion(self, data, debug):
    if debug: logger.debug(f"RESTART -> LC before: {len(data.learned_clauses)}")
    new_learned_clauses = []
    for c in data.learned_clauses:
      if c.lbd <= data.lbd_limit:
        new_learned_clauses.append(c)
      else:
        # remove learned clause from watched
        # structures
        if len(c) == 1:
          data.itc[c[0]].remove(c)
        else:
          data.itc[c.get_w(0)].remove((c, 0))
          data.itc[c.get_w(1)].remove((c, 1))
    data.learned_clauses = new_learned_clauses
    if debug: logger.debug(f"RESTART -> LC after: {len(data.learned_clauses)}")
    return new_learned_clauses

  def _update_on_conflict_limit(self, data, config):
    self._clause_deletion(data, config.debug)
    if config.use_luby:
      data.n_restarts += 1
      k = data.k
      n_restarts = data.n_restarts
      if n_restarts == (1 << k) - 1:
        data.luby_sequence.append(1 << (k - 1))
        data.k += 1
      elif n_restarts >= (1 << (k - 1)) and n_restarts < ((1 << k) - 1):
        data.luby_sequence.append(data.luby_sequence[n_restarts - (1 << (k - 1)) + 1])
      else:
        raise RuntimeError(f"n_restarts: {n_restarts}, data.k: {data.k}")
      data.conflict_limit += data.luby_sequence[n_restarts] * config.base_unit
      # keeping lbd at 2 for the whole run leaves the best results
      # data.lbd_limit *= 1.05
    else:
      data.lbd_limit *= 1.1
      data.conflict_limit *= 1.1

  def _set_decision_lit(self, data: CDCLData, decision, debug, next_unit_prop_lit_int):
    # decision cheat sheet
    # decision == 0 -> dec_var_selection should be done in _set_decision_lit
    # decision == 1 == 001 -> False literal should be selected in _set_decision_lit as the first option
    # decision == 2 == 010 -> True literal should be selected in _set_decision_lit as the first option
    #
    # decision == 4 == 100 -> True literal should be selected in _set_decision_lit as the second option
    # decision == 5 == 101 -> False literal should be selected in _set_decision_lit as the second option
    #
    # when only backjumping (e.g. assertion lvl is 4, so we need to backjump at lvl 4, but not undo
    # unit propagation or dec var selection, then decision > 5 (we add 6 to decision, so its value
    # varies from 7 to 11) and then modulo it by 6 to get it back to where it was)

    if decision == 0:
      var_int, data.decisions[data.current_dec_lvl] = self.dec_var_selection(data)
      data.dec_vars[data.current_dec_lvl] = var_int
    
    if decision < 6:
      data.n_assigned_variables += 1
      var_int = data.dec_vars[data.current_dec_lvl]

      # unit propagation in previous step
      # derived var_int
      if data.assignment[var_int] is not None:
        var_int, decision = self.dec_var_selection(data)
        data.dec_vars[data.current_dec_lvl] = var_int
        data.decisions[data.current_dec_lvl] = decision
      
      lit_int = var_int + var_int + (decision & 1)

      if debug:logger.debug(f"{data.current_dec_lvl}: DEC: {debug_str(lit_int, data.itv)}")
      self.assign_true(lit_int, data.itv, data.assignment, data.itc)
      data.stats.decVars += 1
      data.dec_lvls_of_vars[var_int] = (data.current_dec_lvl, -1)
      data.cs = data.itc[lit_int ^ 1]
      assigned_literals_to_be_added = []
      first_index = -2
    else:
      data.decisions[data.current_dec_lvl] %= 6
      data.cs = data.itc[next_unit_prop_lit_int]
      assigned_literals_to_be_added = data.assigned_literals[data.current_dec_lvl]
      first_index = -2 - len(assigned_literals_to_be_added)
    return first_index, assigned_literals_to_be_added

  def _restart(self, data: CDCLData, config: CDCLConfig):
    if config.debug: logger.debug(f"RESTART")
    data.current_dec_lvl = 1
    # TODO: change to range(data.current_dec_lvl)
    for i in range(len(data.assignment)):
      if data.dec_lvls_of_vars[i][0] > 0:
        data.dec_lvls_of_vars[i] = data.def_dec_lvl
        data.assignment[i] = None
        data.n_assigned_variables -= 1
    for i in range(1, len(data.decisions)):
      data.decisions[i] = 0
    data.generate_new_order_of_vars()
    data.lbd_limit *= 1.1

  def _cdcl(self, data: CDCLData, config: CDCLConfig):
    data.initialize()
    config.base_unit = data.conflict_limit
    next_unit_prop_lit_int = None
    if config.use_luby:
      data.conflict_limit = data.luby_sequence[data.n_restarts] * config.base_unit

    unitPropResult = self.unit_propagation(data, first_index=-1)
    if unitPropResult == UnitPropagationResult.CONFLICT:
      if config.debug and config.use_luby: logger.debug(f"LUBY SEQUENCE: {data.luby_sequence}")
      return SATSolverResult.UNSAT
    if config.debug: logger.debug(f"UP: {debug_str_multi(data.assigned_literals[data.current_dec_lvl], data.itv)}")
    data.current_dec_lvl += 1

    while True:
      decision = data.decisions[data.current_dec_lvl]
      # previous_literals -> previously assigned literals
      first_index, previous_literals = self._set_decision_lit(data, decision, config.debug, next_unit_prop_lit_int)

      # unit propagation
      conflict_clause = self.unit_propagation(data, first_index)
      data.assigned_literals[data.current_dec_lvl] += previous_literals

      # conflict resolution
      if conflict_clause is not None:
        next_unit_prop_lit_int = self._backtrack(conflict_clause, data, config.debug)
        if data.current_dec_lvl == -1:
          return SATSolverResult.UNSAT

        # restart / clause_deletion
        if data.conflict_limit and data.stats.conflicts == int(data.conflict_limit):
          self._update_on_conflict_limit(data, config)
          if config.use_restarts:
            if data.current_dec_lvl == 0:
              continue
            else:
              self._restart(data, config)
        continue

      if config.debug: logger.debug(f"{data.current_dec_lvl}: UP: {debug_str_multi(data.assigned_literals[data.current_dec_lvl], data.itv)}")

      if data.n_assigned_variables == data.n_variables:
        if config.debug: logger.debug(f"RESULT: {debug_str_multi([i + i for i, v in enumerate(data.assignment) if v == 1], data.itv)}")
        if config.debug and config.use_luby: logger.debug(f"LUBY SEQUENCE: {data.luby_sequence}")
        return SATSolverResult.SAT
      data.current_dec_lvl += 1
  
  def cdcl(self, ast_tree_root, debug, conflict_limit=None, lbd_limit=None, use_luby=False, use_restarts=False):
    assignment, itv, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    data = CDCLData(
      itv=itv,
      itc=itc,
      assignment=assignment,
      c=c,
      stats=stats,
      conflict_limit=conflict_limit,
      lbd_limit=lbd_limit,
      n_variables=n_variables
    )
    config = CDCLConfig(
      debug=debug,
      use_luby=use_luby,
      use_restarts=use_restarts
    )
    result = self._cdcl(data, config)

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

