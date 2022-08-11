from satsolver.utils.representation import debug_str
from typing import List

class SATClause:
  def __init__(
    self,
    children: List[int]
  ):
    self.children: List[int] = children
    self.n_satisfied         = 0
    self.n_unsatisfied       = 0

  def debug_str(self, itv) -> str:
    for i, c in enumerate(self.children):
      if i == 0:
        s = f"({debug_str(c, itv)}"
      else:
        s += f", {debug_str(c, itv)}"
    return s + ")" + f"[+{self.n_satisfied};-{self.n_unsatisfied}]"
  
  def __len__(self):
      return len(self.children)
