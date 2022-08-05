from logzero import logger
from satsolver.watched_literals.structures_preparation import prepare_structures

def dpll(ast_tree_root):
  itl, vti, itc, c, stats = prepare_structures(ast_tree_root)

  for clause in c:
    logger.warning(clause)
  
  return