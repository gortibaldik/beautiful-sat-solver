from satsolver.tseitin_encoding.ast_tree import (
    SATClause,
    SATLiteral,
    SATVariable,
)
from typing import List

from satsolver.utils.stats import SATSolverStats


def assign_variable_to_structures(
    variable,
    vti, # variable to int
    itl, # int to literal
    itc, # int to clauses
):
    if len(variable.children) != 0:
        raise RuntimeError(f"`{str(variable)}` is supposed to be a variable")
    var_name = str(variable)
    if var_name not in vti:
        var_int = len(itl)
        vti[var_name] = (var_int, var_int + 1)
        variable = SATVariable(var_int, var_int + 1, var_name)
        itl.append(SATLiteral(variable, True))
        itl.append(SATLiteral(variable, False))
        itc.append([])
        itc.append([])
    
    return vti[var_name]

def assign_literal_to_structures(
    literal,
    vti, # variable to int
    itl, # int to literal
    itc, # int to clauses
):
    # it is a positive literal
    if len(literal.children) == 0:
        pos_int, neg_int = assign_variable_to_structures(literal, vti, itl, itc)
        return pos_int
    elif len(literal.children) == 1:
        pos_int, neg_int = assign_variable_to_structures(literal.children[0], vti, itl, itc)
        return neg_int
    else:
        raise RuntimeError(f"`{str(literal)}` is supposed to be a literal")

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