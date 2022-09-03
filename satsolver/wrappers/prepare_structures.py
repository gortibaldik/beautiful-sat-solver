from satsolver.cdcl.representation import SATClause
import satsolver.dpll.structures_preparation as base

from pysat.solvers import Solver

def transform_clause(clause: SATClause):
  transformed = []

  for literal in clause.children:
    # in the old encoding, 0 is a valid
    # index for var_int, in transformed
    # encoding it is no longer the case
    var_int = (literal >> 1) + 1
    positivity = 1 if (literal & 1) == 0 else -1
    transformed.append(positivity * var_int)
  
  return transformed

def prepare_structures(ast_tree_root, solver: Solver):
  _, _, vti, _, c, _ = base.prepare_structures(ast_tree_root)
  for clause in c:
    solver.add_clause(transform_clause(clause))

  return vti
