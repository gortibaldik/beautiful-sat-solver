from logzero import logger
from satsolver.utils.representation import debug_str
from typing import List

class SATClause:
  """Object representing SATClause as needed for the watched_literals unification"""
  def __init__(
    self,
    children: List[int]
  ):
    self.children: List[int] = children
    self.watched:  List[int] = [None, None]
    self._len:     int       = None

  def __getitem__(self, i: int):
    return self.children[i]
  
  def get_w(self, i):
    """Return i-th watched literal"""
    # if self.watched[i] is None:
    #   return None
    # if len(self.children) <= self.watched[i]:
    #   return None
    return self.children[self.watched[i]]

  def debug_str(self, itv):
    for i, c in enumerate(self.children):
      if i == 0:
        s = f"({debug_str(c, itv)}"
      else:
        s += f", {debug_str(c, itv)}"
    return s + ")"
  
  def __len__(self):
    return  self._len
