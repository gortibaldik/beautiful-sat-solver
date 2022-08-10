from satsolver.watched_literals.representation import SATLiteral
from satsolver.utils.stats import SATSolverStats
from satsolver.utils.structures_preparation import assign_literal_to_structures
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

def prepare_structures(ast_tree_root):
    itl: List[SATLiteral] = [] # int to literal
    vti = {} # variable to int
    itc = [] # int to clauses
    c: List[Tuple[SATClause, int]]   = [] # clauses
    for clause in ast_tree_root.children:
        # it is a literal
        if len(clause.children) <= 1:
            literalInt = assign_literal_to_structures(
                clause,
                vti,
                itl,
                itc,
                SATLiteral
            )
            literal = itl[literalInt]
            satClause = SATClause([literal])
            satClause.watched[0] = 0 # index which is watched in the clause
            satClause._len = len(satClause.children)
            itc[literalInt].append((satClause, 0))
        # it is a disjunction
        else:
            satClause= SATClause([])
            watched_index = 0
            for literal in clause.children:
                literalInt = assign_literal_to_structures(
                    literal,
                    vti,
                    itl,
                    itc,
                    SATLiteral
                )
                literal = itl[literalInt]
                satClause.children.append(literal)
                if watched_index < 2:
                    satClause.watched[watched_index] = watched_index # index which is watched in the clause
                    itc[literalInt].append((satClause, watched_index))
                    watched_index += 1
            satClause._len = len(satClause.children)

        c.append((satClause, -1))
    stats = SATSolverStats()
    return itl, vti, itc, c, stats
