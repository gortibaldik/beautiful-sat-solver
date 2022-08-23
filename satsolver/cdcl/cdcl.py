from typing import List, Protocol, Tuple
from logzero import logger

from satsolver.cdcl.representation import SATClause
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
  
  def _clause_str(
    self,
    clause,
    dec_lvls_of_vars,
    current_dec_lvl,
    assignment,
    itv
  ):
    s = []
    for lit_int in clause.children:
      _s = debug_str(lit_int, itv) + "_@_" + str(dec_lvls_of_vars[lit_int >> 1][0])
      _s += "_"
      var_int = lit_int >> 1
      if dec_lvls_of_vars[var_int][0] == current_dec_lvl:
        _s += "[*]"
      elif assignment[var_int] is None:
        _s += "[?]"
      elif assignment[var_int] == lit_int & 1:
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
  
  def _deep_backtrack(
    self,
    dec_vars,
    decisions,
    assignment,
    assigned_literals,
    dec_lvls_of_vars,
    current_dec_lvl,
    itc,
    itv,
    debug
  ):
    new_dec_lvl = current_dec_lvl
    n_removed_literals = 0
    while decisions[new_dec_lvl] & 1 == 1:
      decisions[new_dec_lvl] = 0
      var_int = dec_vars[new_dec_lvl]
      lit_int = var_int + var_int + 1

      if debug: logger.debug(f"{current_dec_lvl}: UNDEC CL: {debug_str(lit_int, itv)}")
      self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
      n_removed_literals += 1

      # remove unit propagation
      new_dec_lvl -= 1
      if debug:
        logger.debug(f"{new_dec_lvl}: CL UP UNDO: {debug_str_multi(assigned_literals[new_dec_lvl], itv)}")
      self.unassign_multiple(
        assigned_literals[new_dec_lvl],
        assignment,
        dec_lvls_of_vars,
        itc,
        itv
      )
      n_removed_literals += len(assigned_literals[new_dec_lvl])
    
    # we either backtracked to level 0,
    # then the formula is UNSAT
    if new_dec_lvl == 0:

      # we return -1 as the new decision lvl
      # because 0 is a valid value, when backjumping
      # with learning is done
      return n_removed_literals, -1
    
    # else we backtracked to some positive literal
    # decision, so now we need to redo that decision
    var_int = dec_vars[new_dec_lvl]
    lit_int = var_int + var_int
    self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
    decisions[new_dec_lvl] = 1
    n_removed_literals += 1
    return n_removed_literals, new_dec_lvl


  
  def _shallow_backtrack(
    self,
    dec_vars,
    decisions,
    assignment,
    assigned_literals,
    dec_lvls_of_vars,
    current_dec_lvl,
    itc,
    itv,
    debug
  ):
    decision = decisions[current_dec_lvl]
    var_int = dec_vars[current_dec_lvl]
    lit_int = var_int + var_int + (decision & 1)
    new_dec_lvl = current_dec_lvl
    n_removed_literals = 0


    # if we took positive literal
    # then it still remains to check the
    # negative one
    #
    # hence we need to remove unit propagation
    # and retry the second branch 
    if decision & 1 == 0:
      if debug: logger.debug(f"{current_dec_lvl}: UNDEC CL: {debug_str(lit_int, itv)}")
      self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
      n_removed_literals += 1

      # tell the algorithm to take another branch next time
      # on this level
      dec = decisions[new_dec_lvl]
      decisions[new_dec_lvl] = (dec & 1) ^ 1


      # unit propagation was done at the previous level
      new_dec_lvl -= 1

      # decision == 2
      # unit propagation will be taken with
      # next_unit_prop_lit_int
      decisions[new_dec_lvl] += 2
      return n_removed_literals, new_dec_lvl
    else:
      return self._deep_backtrack(
        dec_vars,
        decisions,
        assignment,
        assigned_literals,
        dec_lvls_of_vars,
        current_dec_lvl,
        itc,
        itv,
        debug
      )

  def _backjump(
    self,
    decisions,
    dec_vars,
    assignment,
    dec_lvls_of_vars,
    itc,
    itv,
    assigned_literals,
    assertion_lvl,
    current_dec_lvl,
    debug
  ):
    new_dec_lvl = current_dec_lvl
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
      var_int = dec_vars[new_dec_lvl]
      lit_int = var_int + var_int + (decisions[new_dec_lvl] & 1)

      # backtrack from that level
      if debug: logger.debug(f"{new_dec_lvl}: UNDEC CL: {debug_str(lit_int, itv)}")
      self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
      decisions[new_dec_lvl] = 0
      new_dec_lvl -= 1
      n_removed_literals += 1

      # remove unit propagation
      if debug:
        logger.debug(f"{new_dec_lvl}: CL UP UNDO: {debug_str_multi(assigned_literals[new_dec_lvl], itv)}")
      self.unassign_multiple(
        assigned_literals[new_dec_lvl],
        assignment,
        dec_lvls_of_vars,
        itc,
        itv
      )
      n_removed_literals += len(assigned_literals[new_dec_lvl])

    var_int = dec_vars[new_dec_lvl]
    lit_int = var_int + var_int + (decisions[new_dec_lvl] & 1)
    if debug: logger.debug(f"{new_dec_lvl}: UNDEC CL: {debug_str(lit_int, itv)}")
    self.unassign(lit_int, assignment, dec_lvls_of_vars, itc, itv)
    n_removed_literals += 1

    new_dec_lvl -= 1
    decisions[new_dec_lvl] += 2

    return n_removed_literals, new_dec_lvl


  def _backtrack(
    self,
    conflict_clause,
    assigned_literals,
    current_dec_lvl,
    dec_vars,
    decisions,
    dec_lvls_of_vars,
    learned_clauses,
    antecedents,
    assignment,
    itc,
    itv,
    debug
  ):
    if debug:
      logger.debug(f"{current_dec_lvl}: CONFLICT CLAUSE: {self._clause_str(conflict_clause, dec_lvls_of_vars, current_dec_lvl, assignment, itv)}")
    if current_dec_lvl == 0:
      return -1, 0, 0
    assertive_clause, assertion_lvl = self.conflict_analysis(
      conflict_clause,
      current_dec_lvl,
      dec_lvls_of_vars,
      antecedents,
      itv
    )
    if debug:
      logger.debug(f"{current_dec_lvl}: ASSERTIVE CLAUSE: {self._clause_str(assertive_clause, dec_lvls_of_vars, current_dec_lvl, assignment, itv)}" + \
        f"; AL: {assertion_lvl}")
      #logger.debug(f"{current_dec_lvl}: CL UP UNDO: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")
    self.unassign_multiple(
      assigned_literals[current_dec_lvl],
      assignment,
      dec_lvls_of_vars,
      itc,
      itv
    )
    remove_from_assigned_variables = len(assigned_literals[current_dec_lvl])
    next_unit_prop_lit_int = self._add_to_structures(assertive_clause, learned_clauses, itc)

    if assertion_lvl == current_dec_lvl - 1:
      nrl, new_dec_lvl = self._shallow_backtrack(
        dec_vars,
        decisions,
        assignment,
        assigned_literals,
        dec_lvls_of_vars,
        current_dec_lvl,
        itc,
        itv,
        debug
      )
      remove_from_assigned_variables += nrl
      return new_dec_lvl, next_unit_prop_lit_int, remove_from_assigned_variables
    else:
      nrl, new_dec_lvl = self._backjump(
        decisions,
        dec_vars,
        assignment,
        dec_lvls_of_vars,
        itc,
        itv,
        assigned_literals,
        assertion_lvl,
        current_dec_lvl,
        debug
      )
      remove_from_assigned_variables += nrl
      return new_dec_lvl, next_unit_prop_lit_int, remove_from_assigned_variables

  def _restart(
    self,
    learned_clauses: List[SATClause],
    itc: List[List[SATClause]],
    lbd_limit
  ):
    new_learned_clauses = []
    for c in learned_clauses:
      if c.lbd <= lbd_limit:
        new_learned_clauses.append(c)
      else:
        # remove learned clause from watched
        # structures
        if len(c) == 1:
          itc[c[0]].remove(c)
        else:
          itc[c.get_w(0)].remove((c, 0))
          itc[c.get_w(1)].remove((c, 1))
    
    return new_learned_clauses

  def _cdcl(
    self,
    itv,
    itc,
    assignment,
    c,
    stats: SATSolverStats,
    n_variables,
    debug,
    conflict_limit,
    lbd_limit
  ):
    learned_clauses = []
    def_dec_lvl = (-1, -1)
    size_of_arrays = n_variables + 1
    current_dec_lvl = 0

    while True:
      if current_dec_lvl == -1:
        break

      decisions = [0] * size_of_arrays
      assigned_literals = [None] * size_of_arrays
      dec_vars = [None] * size_of_arrays
      antecedents = [None] * size_of_arrays
      dec_lvls_of_vars = [def_dec_lvl] * size_of_arrays
      cs = c
      next_unit_prop_lit_int = None

      unitPropResult, assigned_literals[current_dec_lvl] = self.unit_propagation(
        itv,
        itc,
        assignment,
        antecedents,
        dec_lvls_of_vars,
        current_dec_lvl,
        c,
        stats,
        first_index=-1
      )
      if unitPropResult == UnitPropagationResult.CONFLICT:
        return SATSolverResult.UNSAT
      if debug: logger.debug(f"UP: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")
      n_assigned_variables = len(assigned_literals[current_dec_lvl])
      current_dec_lvl += 1

      while True:
        decision = decisions[current_dec_lvl]
        if decision == 0:
          var_int = self.dec_var_selection(assignment)
          dec_vars[current_dec_lvl] = var_int
        
        if decision < 2:
          n_assigned_variables += 1
          var_int = dec_vars[current_dec_lvl]

          # unit propagation in previous step
          # derived var_int
          if assignment[var_int] is not None:
            decisions[current_dec_lvl] = 0
            var_int = self.dec_var_selection(assignment)
            dec_vars[current_dec_lvl] = var_int
            lit_int = var_int + var_int
          else:
            lit_int = var_int + var_int + (decision & 1)
          
          if debug:logger.debug(f"{current_dec_lvl}: DEC: {debug_str(lit_int, itv)}")
          self.assign_true(lit_int, itv, assignment, itc)
          stats.decVars += 1
          dec_lvls_of_vars[var_int] = (current_dec_lvl, -1)
          cs = itc[lit_int ^ 1]
          assigned_literals_to_be_added = []
          first_index = -2
        else:
          decisions[current_dec_lvl] &= 1
          cs = itc[next_unit_prop_lit_int]
          assigned_literals_to_be_added = assigned_literals[current_dec_lvl]
          first_index = -2 - len(assigned_literals_to_be_added)

        conflict_clause, assigned_literals[current_dec_lvl] = self.unit_propagation(
          itv,
          itc,
          assignment,
          antecedents,
          dec_lvls_of_vars,
          current_dec_lvl,
          cs,
          stats,
          first_index
        )
        n_assigned_variables += len(assigned_literals[current_dec_lvl])
        assigned_literals[current_dec_lvl] += assigned_literals_to_be_added
        if conflict_clause is not None:
          if conflict_limit and stats.conflicts == conflict_limit:
            # there should be a restart
            logger.info(f"RESTART -> LC before: {len(learned_clauses)}")
            learned_clauses = self._restart(learned_clauses, itc, lbd_limit)
            logger.info(f"RESTART -> LC after: {len(learned_clauses)}")
            lbd_limit *= 1.1
            conflict_limit *= 1.1
            pass
          if decision >= 2:
            decisions[current_dec_lvl + 1] = 0
          stats.conflicts += 1
          current_dec_lvl, next_unit_prop_lit_int, rfav = self._backtrack(
            conflict_clause,
            assigned_literals,
            current_dec_lvl,
            dec_vars,
            decisions,
            dec_lvls_of_vars,
            learned_clauses,
            antecedents,
            assignment,
            itc,
            itv,
            debug
          )
          if current_dec_lvl == -1:
            break
          n_assigned_variables -= rfav
          continue

        if debug: logger.debug(f"{current_dec_lvl}: UP: {debug_str_multi(assigned_literals[current_dec_lvl], itv)}")

        if n_assigned_variables == n_variables:
          logger.debug(f"RESULT: {debug_str_multi([i + i for i, v in enumerate(assignment) if v == 1], itv)}")
          return SATSolverResult.SAT
        current_dec_lvl += 1
      return SATSolverResult.UNSAT
  
  def cdcl(self, ast_tree_root, debug, conflict_limit, lbd_limit):
    assignment, itv, vti, itc, c, stats = self.prepare_structures(ast_tree_root)
    n_variables = len(vti) # vti == variable to integer
    result = self._cdcl(
      itv,
      itc,
      assignment,
      c,
      stats,
      n_variables,
      debug,
      conflict_limit,
      lbd_limit
    )

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
  
  def cdcl_no_restarts(self, ast_tree_root, debug):
    return self.cdcl(ast_tree_root, debug, None, None)
  
  def cdcl_r200_lbd3(self, ast_tree_root, debug):
    return self.cdcl(ast_tree_root, debug, 200, 3)