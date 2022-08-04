from logzero import logger
from satsolver.dpll.assignment import assign_true, get_literal_int, unassign, unassign_multiple
from satsolver.dpll.decision_variable_selection import dec_var_selection
from satsolver.dpll.structures_preparation import prepare_structures
from satsolver.dpll.unit_propagation import unit_propagation
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode, SATLiteral
from satsolver.utils.enums import DecisionVariableResult, UnitPropagationResult, SATSolverResult
from typing import List

from satsolver.utils.stats import SATSolverStats

def __dpll(
    dec_var_int,
    itc, # int to clause
    itl: List[SATLiteral], # int to literal
    c, # clauses
    stats: SATSolverStats
):
    cs = c # cs == clauses to search
    if dec_var_int is not None:
        cs = itc[dec_var_int]
    unitPropResult, assigned_literals = unit_propagation(itc, cs, c, stats)

    if unitPropResult == UnitPropagationResult.CONFLICT:
        return SATSolverResult.UNSAT, assigned_literals
    elif unitPropResult == UnitPropagationResult.ALL_SATISFIED:
        return SATSolverResult.SAT, None

    decVarResult, pos_int, neg_int = dec_var_selection(itl, itc)

    if decVarResult == DecisionVariableResult.FAILURE:
        logger.warning("DecVarResult is FAILURE")
        return SATSolverResult.UNSAT

    satResultPos = _dpll(pos_int, itc, itl, c, stats)
    if satResultPos == SATSolverResult.SAT:
        return satResultPos, None

    satResultNeg = _dpll(neg_int, itc, itl, c, stats)
    if satResultNeg == SATSolverResult.SAT:
        return satResultNeg, None

    return SATSolverResult.UNSAT, assigned_literals

def _dpll(
    dec_var_int,
    itc, # int to clause
    itl: List[SATLiteral], # int to literal
    c, # clauses
    stats: SATSolverStats
):
    """
    Assigns true to literal which has index `dec_var_int` in table `itl` (int to literal). Calls `__dpll`.
    Also unassigns in case of `UNSAT` (e.g. removes the need for unassignments in all cases where `__dpll`
    can return `UNSAT`)
    """
    other_int, literal = None, None
    if dec_var_int is not None:
        literal = itl[dec_var_int]
        lit_int, other_int, is_positive = get_literal_int(literal)
        result = assign_true(literal, itc)
        stats.decVars += 1
        if result == UnitPropagationResult.CONFLICT:
            unassign(literal, itc)
            return SATSolverResult.UNSAT
    result, assigned_variables = __dpll(other_int, itc, itl, c, stats)
    if result == SATSolverResult.UNSAT:
        unassign_multiple(assigned_variables, itc)
        if literal is not None:
            unassign(literal, itc)

    return result

def dpll(ast_tree_root: ASTAbstractNode):
    itl, vti, itc, c, stats = prepare_structures(ast_tree_root)
    result = _dpll(None, itc, itl, c, stats)

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