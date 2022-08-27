from dataclasses import dataclass

@dataclass
class SATSolverStats:
  unitPropCheckedClauses: int = 0
  unitProps: int              = 0
  decVars: int                = 0
  conflicts: int              = 0
  learnedClausesPeak: int     = 0

  def update(self, stats):
    self.unitProps              += stats.unitProps
    self.decVars                += stats.decVars
    self.unitPropCheckedClauses += stats.unitPropCheckedClauses
    self.conflicts              += stats.conflicts
    self.learnedClausesPeak     += stats.learnedClausesPeak
  
  def divide(self, total):
    self.unitProps /= total
    self.unitPropCheckedClauses /= total
    self.decVars /= total
    self.conflicts /= total
    self.learnedClausesPeak /= total
  
  def __repr__(self):
    return f"decs: {self.decVars}; unit: {self.unitProps}; unit_checked: " +\
           f"{self.unitPropCheckedClauses}; conflicts: {self.conflicts}; learnedClausesPeak: {self.learnedClausesPeak}"