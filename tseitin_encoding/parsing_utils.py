from tseitin_encoding.symbols import Symbols
from tseitin_encoding.ast_tree import ASTNodeFactory
import tseitin_encoding.word_utils as wu

def invalid_start_index(formula, start_index):
    return f"invalid start index: {start_index}, len(formula): {len(formula)}"

def parse_variable(formula: str, start_index):
    if start_index >= len(formula):
        raise RuntimeError(f"PARSE_VARIABLE: {invalid_start_index(formula, start_index)}")
    if not wu.is_letter(formula[start_index]):
        raise RuntimeError(f"PARSE_VARIABLE: {formula[start_index:]}")
    result_index = start_index
    result_word = ""
    for c in formula[start_index:]:
        if not wu.is_letter(c) and not wu.is_digit(c):
            return result_index, result_word
        result_word += c
        result_index += 1
    return result_index, result_word

def parse_whitespace(formula: str, start_index):
    while start_index < len(formula) and wu.is_whitespace(formula[start_index]):
        start_index += 1
    return start_index

def parse_formula(formula: str):
    """Create a list of tokens from string representation in SMT-LIB format"""
    symbol_list = []
    current_index = 0
    while current_index < len(formula):
        current_index = parse_whitespace(formula, current_index)
        if current_index >= len(formula):
            return current_index
        c = formula[current_index]
        if c == '(':
            symbol_list.append((Symbols.LEFT_PARENTHESE, None))
            current_index += 1
        elif c == ')':
            symbol_list.append((Symbols.RIGHT_PARENTHESE, None))
            current_index += 1
        elif wu.is_letter(c):
            current_index, word = parse_variable(formula, current_index)
            if word == 'or':
                symbol_list.append((Symbols.OR, None))
            elif word == 'not':
                symbol_list.append((Symbols.NOT, None))
            elif word == 'and':
                symbol_list.append((Symbols.AND, None))
            else:
                symbol_list.append((Symbols.VARIABLE, word))
        else:
            raise RuntimeError(f"PARSE_FORMULA: invalid char at position {current_index}: {c}")
    
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