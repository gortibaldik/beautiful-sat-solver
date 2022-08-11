from satsolver.utils.representation import SATLiteral
from typing import List

class SATClause:
    def __init__(
        self,
        children: List[SATLiteral]
    ):
        self.children: List[SATLiteral] = children
        self.n_satisfied                = 0
        self.n_unsatisfied              = 0

    def __repr__(self):
        for i, c in enumerate(self.children):
            if i == 0:
                s = f"({str(c)}"
            else:
                s += f", {c}"
        return s + ")" + f"[+{self.n_satisfied};-{self.n_unsatisfied}]"
    
    def __len__(self):
        return len(self.children)
