from enum import Enum

class UnitPropagationResult(Enum):
  NOTHING_FOUND = 0
  CONFLICT      = 1
  UNIT_FOUND    = 2
  SUCCESS       = 3
  ALL_SATISFIED = 4

class DecisionVariableResult(Enum):
  SUCCESS = 0
  FAILURE = 1

class SATSolverResult(Enum):
  SAT = "SAT"
  UNSAT = "UNSAT"
