import satsolver.watched_literals.representation as wl_repre

from typing import List

class SATClause(wl_repre.SATClause):
  def __init__(
    self,
    children: List[int],
    lbd: int
  ):
    super().__init__(children)
    self.lbd = lbd