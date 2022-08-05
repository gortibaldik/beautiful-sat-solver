import satsolver.utils.representation as base_repre
from typing import List

class SATLiteral(base_repre.SATLiteral):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.watched_index = None

class SATClause:
  def __init__(
    self,
    children: List[SATLiteral]
  ):
    self.children: List[SATLiteral] = children
    self.watched:  int              = [None, None]
  
  @staticmethod
  def lts(literal: SATLiteral):
    """Literal to Sign"""
    if literal is None or not literal.is_assigned():
      return "?"
    elif literal.is_satisfied():
      return "+"
    else:
      return "-"

  def __repr__(self):
    for i, c in enumerate(self.children):
      if i == 0:
        s = f"({c}"
      else:
        s += f", {c}"
    wl_0 = self.children[self.watched[0]]
    if self.watched[1]:
      wl_1 = self.children[self.watched[1]]
    else:
      wl_1 = None 
    return s + ")" + "\t[" +\
      self.lts(wl_0) + f"({wl_0}); " + \
      self.lts(wl_1) + f"({wl_1})]"
