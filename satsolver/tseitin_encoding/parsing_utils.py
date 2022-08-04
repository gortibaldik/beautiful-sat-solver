from satsolver.tseitin_encoding.symbols import Symbols
from satsolver.tseitin_encoding.ast_tree import ASTNodeFactory

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

def not_stack_correct(stack, symbol_list, index):
    if  index == 0 or \
        symbol_list[index - 1][0] != Symbols.LEFT_PARENTHESE or \
        stack[0][0] not in [Symbols.VARIABLE, Symbols.PROCESSED] \
        :
        return True
    if  symbol_list[index][0] == Symbols.NOT and \
        stack[1][0] != Symbols.RIGHT_PARENTHESE:
        return True
    
    if  symbol_list[index][0] in [ Symbols.AND, Symbols.OR] and \
        (   stack[1][0] not in [Symbols.VARIABLE, Symbols.PROCESSED] or \
            stack[2][0] != Symbols.RIGHT_PARENTHESE \
        ):
        return True
    return False

def create_binary_node(symbol_list, stack, index):
    if not_stack_correct(stack, symbol_list, index):
        raise RuntimeError(f"stack: {stack}" + "\n" + f"symbol_list[{index}]: {symbol_list[index]}")

    tp = symbol_list[index][0]
    node = ASTNodeFactory.get_node(tp, None)

    lnc = len(node.children)
    for i in range(lnc):
        if stack[i][0] == Symbols.VARIABLE:
            node.children[i] = ASTNodeFactory.get_node(Symbols.VARIABLE, stack[i][1])
        else:
            node.children[i] = stack[i][1]

    index -= 2 # left parenthese
    stack = stack[lnc + 1:]
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
        
        if type in [Symbols.AND, Symbols.OR, Symbols.NOT]:
            index, stack = create_binary_node(symbol_list, stack, index)
            continue
    
    if len(stack) != 1:
        raise RuntimeError(str(stack))
    
    root = stack[0][1]
    return root