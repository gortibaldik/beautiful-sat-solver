from satsolver.dpll.representation import SATClause
from satsolver.utils.representation import SATLiteral
from satsolver.utils.stats import SATSolverStats
from satsolver.utils.structures_preparation import assign_literal_to_structures
from typing import List

def prepare_structures(ast_tree_root):
    itl: List[SATLiteral] = [] # int to literal
    vti = {} # variable to int
    itc = [] # int to clauses
    c: List[SATClause]   = [] # clauses
    for clause in ast_tree_root.children:
        # it is a literal
        if len(clause.children) <= 1:
            literalInt = assign_literal_to_structures(clause, vti, itl, itc)
            satClause = SATClause([itl[literalInt]])
            itc[literalInt].append(satClause)
        # it is a disjunction
        else:
            satClause= SATClause([])
            for literal in clause.children:
                literalInt = assign_literal_to_structures(literal, vti, itl, itc)
                satClause.children.append(itl[literalInt])
                itc[literalInt].append(satClause)

        c.append(satClause)
    stats = SATSolverStats()
    return itl, vti, itc, c, stats

def health_check(c):
    for clause in c:
        if clause.n_satisfied != 0 or clause.n_unsatisfied != 0:
          raise RuntimeError(f"SATSolverResult == UNSAT while there are still assignments pending!")
