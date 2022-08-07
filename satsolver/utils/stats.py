from dataclasses import dataclass

@dataclass
class SATSolverStats:
  unitPropCheckedClauses: int = 0
  unitProps: int              = 0
  decVars: int                = 0

  def update(self, stats):
    self.unitProps              += stats.unitProps
    self.decVars                += stats.decVars
    self.unitPropCheckedClauses += stats.unitPropCheckedClauses
  
  def divide(self, total):
    self.unitProps /= total
    self.unitPropCheckedClauses /= total
    self.decVars /= total