from typing import List
from satsolver.dpll.unit_propagation import is_everything_satisfied

from satsolver.tseitin_encoding.ast_tree import SATClause, SATLiteral
from satsolver.utils.enums import DecisionVariableResult


def dec_var_selection(
  itl: List[SATLiteral], # int to literal
  itc: List[SATClause]   # int to clause
):
  """
  Select first unassigned variable
  """
  for l in itl:
    if l.satVariable.truth_value is None:
      return DecisionVariableResult.SUCCESS, \
             l.satVariable.positive_int, \
             l.satVariable.negative_int
  return DecisionVariableResult.FAILURE, None, None