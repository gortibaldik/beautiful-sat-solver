from tseitin_encoding.symbols import Symbols

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
    def __init__(self, type):
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

class ASTNaryNode(ASTAbstractNode):
    def __init__(self, type):
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
        s = "( "
        for i, c in enumerate(self.children):
            if i == 0:
                s += str(c)
            else:
                s += f" {self.type.value} {c}"
        s += " )"
        return s

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

class ASTBinaryNode(ASTNaryNode):
    def __init__(self, type) -> None:
        super().__init__(type)
        self.children = [ None, None ]

class ASTUnaryNode(ASTNaryNode):
    def __init__(self, type) -> None:
        super().__init__(type)
        self.children = [ None ]
    
    def __str__(self) -> str:
        s = f"{self.type.value} {self.children[0]}"
        return s

class ASTVariableNode(ASTAbstractNode):
    def __init__(self, type, value) -> None:
        super().__init__(type)
        self._value = value
    
    def __str__(self):
        return str(self._value)
    
    def count(self):
        return {
            "variables": set([self._value]),
            "subformulas": 0
        }
