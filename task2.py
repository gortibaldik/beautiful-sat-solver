import os
from argparse import ArgumentParser
from enum import Enum
from logzero import logger
from task1 import read_formula, tseitin_encoding, set_debug_level
from tseitin_encoding.ast_tree import ASTNaryNode, ASTUnaryNode, ASTVariableNode
from tseitin_encoding.symbols import Symbols
from tseitin_encoding.tseitin_transformation import log_node_info

class Extensions(Enum):
    DIMACS=".cnf"
    SMTLIB=".sat"

def recognize_file_extension(file_name: str):
    filename, file_extension = os.path.splitext(file_name)
    for extension in Extensions:
        if file_extension == extension.value:
            return extension
    
    raise RuntimeError("Invalid extension for input file: either DIMACS (.cnf) or SMTLIB (.sat)")

def read_dimacs(formula: str):
    var_names = {}
    conjunction = ASTNaryNode(Symbols.AND)
    for line in formula.split('\n'):
        if len(line) == 0:
            continue
        symbols = line.strip().split()
        if symbols[0] == "c":
            # comments with variable names
            if len(symbols) != 3 or len(symbols) != 4:
                logger.debug(f"Unexpected comment line: {line}")
            i1, i2 = 1, 2
            if symbols[1] == "MAIN":
                i1, i2 = 2, 3
                if len(symbols) != 4:
                    logger.debug(f"Unexpected comment line: {line}")
            elif len(symbols) != 3:
                logger.debug(f"Unexpected comment line: {line}")
            var_names[symbols[i1]] = symbols[i2]
            continue

        if symbols[0] == "p":
            if len(symbols) != 4:
                raise RuntimeError(f"Unexpected comment line: {line}")
            expected_vars = int(symbols[2])
            expected_clauses = int(symbols[3])
            continue
        
        disjunction = ASTNaryNode(Symbols.OR)
        for symbol in symbols:
            if symbol[0] == '-':
                var_node = ASTVariableNode(Symbols.VARIABLE, var_names[symbol[1:]])
                node = ASTUnaryNode(Symbols.NOT)
                node.children = [var_node]
            else:
                node = ASTVariableNode(Symbols.VARIABLE, var_names[symbol])
            disjunction.children.append(node)
        conjunction.children.append(disjunction)
    
    log_node_info(conjunction)
    logger.info(f"EXPECTED: 'variables': {expected_vars}, 'subformulas': {expected_clauses + 1}")
    return conjunction


def create_parser():
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str, help="Input file in DIMACS (.cnf) or in SMTLIB (.sat) format.")
    parser.add_argument('--debug', action='store_true')
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    set_debug_level(args.debug)
    extension = recognize_file_extension(args.input_file)
    formula = read_formula(args.input_file)
    if extension == Extensions.SMTLIB:
        ast_tree_root = tseitin_encoding(formula, nnf_reduce_implications=True)
    elif extension == Extensions.DIMACS:
        ast_tree_root = read_dimacs(formula)