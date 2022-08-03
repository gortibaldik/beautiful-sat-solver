from logzero import logger
from satsolver.dpll.assignment import assign_true, get_literal_int, unassign, unassign_multiple
from satsolver.dpll.decision_variable_selection import dec_var_selection
from satsolver.dpll.structures_preparation import prepare_structures
from satsolver.dpll.unit_propagation import unit_propagation
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode, SATLiteral
from satsolver.utils.enums import DecisionVariableResult, UnitPropagationResult, SATSolverResult
from typing import List

def __dpll(
    dec_var_int,
    itc,
    itl: List[SATLiteral],
    c
):
    cs = c # cs == clauses to search
    if dec_var_int is not None:
        cs = itc[dec_var_int]
    unitPropResult, assigned_literals = unit_propagation(itc, cs, c)

    if unitPropResult == UnitPropagationResult.CONFLICT:
        return SATSolverResult.UNSAT, assigned_literals
    elif unitPropResult == UnitPropagationResult.ALL_SATISFIED:
        return SATSolverResult.SAT, None

    decVarResult, pos_int, neg_int = dec_var_selection(itl, itc)

    if decVarResult == DecisionVariableResult.FAILURE:
        logger.warning("DecVarResult is FAILURE")
        return SATSolverResult.UNSAT

    satResultPos = _dpll(pos_int, itc, itl, c)
    if satResultPos == SATSolverResult.SAT:
        return satResultPos, None

    satResultNeg = _dpll(neg_int, itc, itl, c)
    if satResultNeg == SATSolverResult.SAT:
        return satResultNeg, None

    return SATSolverResult.UNSAT, assigned_literals

def _dpll(
    dec_var_int,
    itc,
    itl: List[SATLiteral],
    c
):
    other_int, literal = None, None
    if dec_var_int is not None:
        literal = itl[dec_var_int]
        lit_int, other_int, is_positive = get_literal_int(literal)
        result = assign_true(literal, itc)
        if result == UnitPropagationResult.CONFLICT:
            unassign(literal, itc)
            return SATSolverResult.UNSAT
    result, assigned_variables = __dpll(other_int, itc, itl, c)
    if result == SATSolverResult.UNSAT:
        unassign_multiple(assigned_variables, itc)
        if literal is not None:
            unassign(literal, itc)

    return result

def dpll(ast_tree_root: ASTAbstractNode):
    itl, vti, itc, c = prepare_structures(ast_tree_root)
    result = _dpll(None, itc, itl, c)

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



    return result.value, model, 0, 0