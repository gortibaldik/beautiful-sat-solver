class SATVariable:
    def __init__(self, positive_int: int, negative_int: int, name: str):
        self.positive_int = positive_int
        self.negative_int = negative_int
        self.name         = name
        self.truth_value  = None
    def __repr__(self):
        return self.name

class SATLiteral:
    def __init__(
        self,
        satVariable: SATVariable,
        positivity_of_literal
    ):
        self.satVariable: SATVariable = satVariable
        self.positive                 = positivity_of_literal
    def __repr__(self):
        s = "" if self.positive else "NOT "
        s += str(self.satVariable)
        return s