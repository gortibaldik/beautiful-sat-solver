class SATVariable:
    def __init__(self, positive_int: int, negative_int: int, name: str):
        self.positive_int       = positive_int
        self.negative_int       = negative_int
        self.name               = name
        self.truth_value: bool  = None
    def __repr__(self):
        return self.name

class SATLiteral:
  def __init__(
      self,
      satVariable: SATVariable,
      positivity_of_literal
  ):
      self.satVariable: SATVariable = satVariable
      self.positive: bool           = positivity_of_literal

  def _lts(self):
    """Literal to Sign"""
    if not self.is_assigned():
      return "?"
    elif self.is_satisfied():
      return "+"
    else:
      return "-"
    
  def __repr__(self):
    s = f"[{self._lts()}]"
    s += "" if self.positive else "NOT "
    s += str(self.satVariable)
    return s

  def is_assigned(self):
    return self.satVariable.truth_value is not None

  def is_satisfied(self):
    return self.positive == self.satVariable.truth_value

  def is_unsatisfied(self):
    return self.is_assigned() and not self.is_satisfied()