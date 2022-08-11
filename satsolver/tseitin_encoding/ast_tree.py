from typing import List
from satsolver.tseitin_encoding.symbols import Symbols

class ASTNodeFactory:
    @staticmethod
    def get_node(type: Symbols, value):
        if type in [Symbols.AND, Symbols.OR]:
            return ASTBinaryNode(type)
        elif type == Symbols.NOT:
            return ASTUnaryNode(type)
        else:
            return ASTVariableNode(type, value)

class ASTAbstractNode:
    def __init__(self, type: Symbols):
        self.children = []
        self._type: Symbols = type
    
    @property
    def n_children(self):
        return len(self.children)
    
    @property
    def type(self):
        return self._type

    def get_subformulas(self):
        return None
    
    def count(self):
        pass
    
    def copy(self):
        pass

class ASTNaryNode(ASTAbstractNode):
    def __init__(self, type: Symbols):
        super().__init__(type)
        self.children = []
    
    def get_subformulas(self):
        subformulas = []
        subformulas.append(self)
        for c in self.children:
            sf = c.get_subformulas()
            if sf is not None:
                subformulas += sf
        return subformulas
    
    def __str__(self) -> str:
        s = ""
        for i, c in enumerate(self.children):
            if i == 0:
                s += str(c)
            else:
                s += f" {self.type.value} {c}"
        return f"( {s} )"

    def count(self):
        result = {
            "variables": set(),
            "subformulas": 1 if len(self.children) > 1  else 0
        }
        for c in self.children:
            res_c = c.count()
            result["variables"] = result["variables"].union(res_c["variables"])
            result["subformulas"] += res_c["subformulas"]
        return result
    
    def copy(self):
        node = ASTNaryNode(type=self._type)
        for c in self.children:
            new_c = c.copy()
            node.children.append(new_c)
        return node

class ASTBinaryNode(ASTNaryNode):
    def __init__(self, type: Symbols) -> None:
        super().__init__(type)
        self.children = [ None, None ]

class ASTUnaryNode(ASTNaryNode):
    def __init__(self, type: Symbols) -> None:
        super().__init__(type)
        self.children = [ None ]
    
    def __str__(self) -> str:
        s = f"{self.type.value} {self.children[0]}"
        return s
    
    def copy(self):
        node = ASTUnaryNode(type=self._type)
        new_c = self.children[0].copy()
        node.children = [new_c]
        return node

class ASTVariableNode(ASTAbstractNode):
    def __init__(self, type: Symbols, value) -> None:
        super().__init__(type)
        self._value = value
    
    def __str__(self):
        return str(self._value)
    
    def count(self):
        return {
            "variables": set([self._value]),
            "subformulas": 0
        }
    
    def copy(self):
        return ASTVariableNode(self._type, self._value)
        