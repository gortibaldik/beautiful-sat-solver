from satsolver.utils.stats import SATSolverStats
from satsolver.watched_literals.representation import SATClause
from typing import List, Tuple

from satsolver.utils.representation import SATLiteral

def get_literal_int(literal: SATLiteral):
  if literal.positive:
    lit_int = literal.satVariable.positive_int
    other_int = literal.satVariable.negative_int
  else:
    lit_int = literal.satVariable.negative_int
    other_int = literal.satVariable.positive_int
  return lit_int, other_int

def assign_variable_to_structures(
    variable,
    itv, # int to variable name
    vti, # variable to int
    assignment,
    itc, # int to clauses
):
    if len(variable.children) != 0:
        raise RuntimeError(f"`{str(variable)}` is supposed to be a variable")
    var_name = str(variable)
    if var_name not in vti:
        var_int = len(assignment)
        vti[var_name] = var_int
        itv.append(var_name)
        assignment.append(None)
        itc.append([])
        itc.append([])
    
    return vti[var_name]

def assign_literal_to_structures(
    literal,
    itv, # int to variable name
    vti, # variable to int
    assignment,
    itc, # int to clauses
):
    # it is a positive literal
    if len(literal.children) == 0:
        # vix == variable index
        vix = assign_variable_to_structures(
            literal,
            itv,
            vti,
            assignment,
            itc
        )
        return vix << 1
    elif len(literal.children) == 1:
        vix = assign_variable_to_structures(
            literal.children[0],
            itv,
            vti,
            assignment,
            itc,
        )
        return vix << 1 | 1
    else:
        raise RuntimeError(f"`{str(literal)}` is supposed to be a literal")

def prepare_structures(ast_tree_root):
    assignment: List[bool] = []
    itv = [] # int to variable name
    vti = {} # variable to int
    itc = [] # int to clauses
    c: List[Tuple[SATClause, int]]   = [] # clauses
    for clause in ast_tree_root.children:
        # it is a literal
        if len(clause.children) <= 1:
            literalInt = assign_literal_to_structures(
                clause,
                itv,
                vti,
                assignment,
                itc,
            )
            satClause = SATClause([literalInt])
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
                    itv,
                    vti,
                    assignment,
                    itc
                )
                satClause.children.append(literalInt)
                if watched_index < 2:
                    satClause.watched[watched_index] = watched_index # index which is watched in the clause
                    itc[literalInt].append((satClause, watched_index))
                    watched_index += 1
            satClause._len = len(satClause.children)

        c.append((satClause, -1))
    stats = SATSolverStats()
    return assignment, itv, vti, itc, c, stats
