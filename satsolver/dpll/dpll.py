
from satsolver.dpll.pure_literal_elimination import pure_literal_elimination
from satsolver.dpll.unit_propagation import unit_propagation
from logzero import logger
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode
from satsolver.tseitin_encoding.tseitin_transformation import negate_literal

def combine_assignments(unit_assignment, pure_elimination_assignment):
    if len(unit_assignment) < len(pure_elimination_assignment):
        return combine_assignments(pure_elimination_assignment, unit_assignment)
    
    for variable, assignment in pure_elimination_assignment.items():
        unit_assignment[variable] = assignment
    
    return unit_assignment

def remove_clauses_from_root(ast_tree_root: ASTAbstractNode, removed_clauses):
    for clause_idx in sorted(removed_clauses, reverse=True):
        ast_tree_root.children.pop(clause_idx)

def choose_literal(ast_tree_root: ASTAbstractNode):
    first_child = ast_tree_root.children[0]
    # first_child must have at least 2 children, because this is run
    # right after unit propagation
    if len(first_child.children) <= 1:
        raise RuntimeError(f"Error in DPLL - found child {first_child} with too little children!")
    
    return first_child.children[0]

def dpll(ast_tree_root: ASTAbstractNode):
    unit_assignment, vcm, removed_clauses = unit_propagation(ast_tree_root)
    if unit_assignment == None:
        return "UNSAT", None, 0, 0
    unit_propagation_steps = len(unit_assignment)

    pure_elimination_assignment = pure_literal_elimination(vcm, removed_clauses, unit_assignment)
    
    remove_clauses_from_root(ast_tree_root, removed_clauses)
    model = combine_assignments(unit_assignment, pure_elimination_assignment)
    if len(ast_tree_root.children) == 0:
        return "SAT", model, 0, unit_propagation_steps
    
    decision_literal = choose_literal(ast_tree_root)
    logger.debug(f"-- DECISION: {decision_literal}")

    new_ast_tree_root = ast_tree_root.copy()
    new_ast_tree_root.children.append(decision_literal)
    result, model_recursion, number_of_decisions_rec1, unit_propagation_steps_rec1 = dpll(new_ast_tree_root)

    number_of_decisions_rec2, unit_propagation_steps_rec2 = 0, 0
    if result == "UNSAT":
        ast_tree_root.children.append(negate_literal(decision_literal))
        result, model_recursion, number_of_decisions_rec2, unit_propagation_steps_rec2 = dpll(ast_tree_root)

    if result != "UNSAT":
        model = combine_assignments(model, model_recursion)
    else:
        model = None

    return  result, \
            model, \
            1 + number_of_decisions_rec1 + number_of_decisions_rec2, \
            unit_propagation_steps + unit_propagation_steps_rec1 + unit_propagation_steps_rec2