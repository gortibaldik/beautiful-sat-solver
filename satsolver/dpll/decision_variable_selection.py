from satsolver.utils.representation import SATLiteral
from satsolver.utils.enums import DecisionVariableResult
from typing import List


def dec_var_selection(
  itl: List[SATLiteral], # int to literal
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