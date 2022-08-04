from enum import Enum

class Symbols(Enum):
    LEFT_PARENTHESE = 'rp'
    RIGHT_PARENTHESE = 'lp'
    AND = 'A'
    OR = 'V'
    NOT = 'NOT'
    EQUIVALENCE = '<=>'
    IMPLICATION = '=>'
    VARIABLE = 'var'
    PROCESSED = 'processed'