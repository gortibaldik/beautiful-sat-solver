from tseitin_encoding.symbols import Symbols
from tseitin_encoding.ast_tree import ASTNodeFactory

symbols_mapping = {
    "not": Symbols.NOT,
    "and": Symbols.AND,
    "or": Symbols.OR,
    "(": Symbols.LEFT_PARENTHESE,
    ")": Symbols.RIGHT_PARENTHESE
}

def to_symbol(symbol: str):
    if symbol in [ "not", "and", "or", "(", ")" ]:
        return (symbols_mapping[symbol], symbol)
    if not symbol.isalnum() or not symbol[0].isalpha():
        raise RuntimeError(f"Wrong symbol: {symbol}")
    return (Symbols.VARIABLE, symbol)

def parse_formula(formula: str):
    """Create a list of tokens from string representation in SMT-LIB format"""
    formula = formula.replace("(", "( ").replace(")", " )")
    symbol_list = [to_symbol(s) for s in formula.split() if len(s) > 0]

    return symbol_list

def create_not_node(symbol_list, stack, index):
    if len(stack) < 2 or \
        index == 0 or \
        symbol_list[index - 1][0] != Symbols.LEFT_PARENTHESE or \
        stack[0][0] not in [Symbols.VARIABLE, Symbols.PROCESSED] or \
        stack[1][0] != Symbols.RIGHT_PARENTHESE \
        :
        raise RuntimeError("NOT")

    tp = symbol_list[index][0]
    node = ASTNodeFactory.get_node(tp, None)

    child = stack[0][1]
    if stack[0][0] == Symbols.VARIABLE:
        child = ASTNodeFactory.get_node(Symbols.VARIABLE, child)
    node.children[0] = child

    index -= 2 # left parenthese
    stack = stack[2:]
    stack = [(Symbols.PROCESSED, node)] + stack
    return index, stack

def create_and_or_node(symbol_list, stack, index):
    if len(stack) < 3 or \
        index == 0 or \
        symbol_list[index - 1][0] != Symbols.LEFT_PARENTHESE or \
        stack[0][0] not in [Symbols.VARIABLE, Symbols.PROCESSED] or \
        stack[1][0] not in [Symbols.VARIABLE, Symbols.PROCESSED] or \
        stack[2][0] != Symbols.RIGHT_PARENTHESE \
        :
        raise RuntimeError("AND/OR")

    tp = symbol_list[index][0]
    node = ASTNodeFactory.get_node(tp, None)

    leftChild = stack[0][1]
    if stack[0][0] == Symbols.VARIABLE:
        leftChild = ASTNodeFactory.get_node(Symbols.VARIABLE, leftChild)

    rightChild = stack[1][1]
    if stack[1][0] == Symbols.VARIABLE:
        rightChild = ASTNodeFactory.get_node(Symbols.VARIABLE, rightChild)

    node.children[0] = leftChild
    node.children[1] = rightChild

    index -= 2 # left parenthese
    stack = stack[3:]
    stack = [(Symbols.PROCESSED, node)] + stack
    return index, stack

def create_abstract_syntax_tree(formula: str):
    """Non-recursive formula tree construction"""
    symbol_list = parse_formula(formula)

    index = len(symbol_list) - 1
    stack = []
    while index > -1:
        type = symbol_list[index][0]
        if type in [Symbols.RIGHT_PARENTHESE, Symbols.VARIABLE]:
            stack = [symbol_list[index]] + stack
            index -= 1
            continue
        
        if type == Symbols.NOT:
            index, stack = create_not_node(symbol_list, stack, index)
            continue
        
        if type in [Symbols.AND, Symbols.OR]:
            index, stack = create_and_or_node(symbol_list, stack, index)
            continue
    
    if len(stack) != 1:
        raise RuntimeError(str(stack))
    
    root = stack[0][1]
    return root