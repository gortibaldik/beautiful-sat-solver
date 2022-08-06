from logzero import logger
from satsolver.utils.representation import SATLiteral
from typing import List

class SATClause:
  """Object representing SATClause as needed for the watched_literals unification"""
  def __init__(
    self,
    children: List[SATLiteral]
  ):
    self.children: List[SATLiteral] = children
    self.watched:  int              = [None, None]

  def __getitem__(self, i: int):
    return self.children[i]
  
  def get_w(self, i):
    """Return i-th watched literal"""
    if self.watched[i] is None:
      logger.debug(f"self.watched[{i}] is None")
      return None
    if len(self.children) <= self.watched[i]:
      logger.debug(f"len(self.children) == {len(self.children)}, self.watched[{i}] == {self.watched[i]}")
      return None
    return self.children[self.watched[i]]

  def __repr__(self):
    for i, c in enumerate(self.children):
      if i == 0:
        s = f"({c}"
      else:
        s += f", {c}"
    wl_0 = self.get_w(0)
    wl_1 = self.get_w(1)
    return s + ")" + "\t[" +\
      f"({wl_0}); " + f"({wl_1})]"
  
  def __len__(self):
    return len(self.children)
