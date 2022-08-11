from satsolver.dpll.representation import SATClause
from satsolver.utils.stats import SATSolverStats
from satsolver.utils.structures_preparation import assign_literal_to_structures
from typing import List

def prepare_structures(ast_tree_root):
    assignment: List[bool] = []
    itv = [] # int to variable
    vti = {} # variable to int
    itc = [] # int to clauses
    c: List[SATClause]   = [] # clauses
    for clause in ast_tree_root.children:
        # it is a literal
        if len(clause.children) <= 1:
            literalInt = assign_literal_to_structures(clause, itv, vti, assignment, itc)
            satClause = SATClause([literalInt])
            itc[literalInt].append(satClause)
        # it is a disjunction
        else:
            satClause= SATClause([])
            for literal in clause.children:
                literalInt = assign_literal_to_structures(literal, itv, vti, assignment, itc)
                satClause.children.append(literalInt)
                itc[literalInt].append(satClause)

        c.append(satClause)
    stats = SATSolverStats()
    return assignment, itv, vti, itc, c, stats

def health_check(c):
    for clause in c:
        if clause.n_satisfied != 0 or clause.n_unsatisfied != 0:
          raise RuntimeError(f"SATSolverResult == UNSAT while there are still assignments pending!")
