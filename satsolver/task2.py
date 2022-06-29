import os
from argparse import ArgumentParser
from enum import Enum
from logzero import logger
from satsolver.task1 import read_formula, tseitin_encoding, set_debug_level, add_parser_debug_levels
from satsolver.dpll.dpll import dpll
from timeit import default_timer as timer
from satsolver.tseitin_encoding.ast_tree import ASTNaryNode, ASTUnaryNode, ASTVariableNode
from satsolver.tseitin_encoding.symbols import Symbols
from satsolver.tseitin_encoding.tseitin_transformation import log_node_info

class Extensions(Enum):
    DIMACS=".cnf"
    SMTLIB=".sat"

def recognize_file_extension(file_name: str):
    filename, file_extension = os.path.splitext(file_name)
    for extension in Extensions:
        if file_extension == extension.value:
            return extension
    
    raise RuntimeError("Invalid extension for input file: either DIMACS (.cnf) or SMTLIB (.sat)")

def create_variable_node(node_str: str):
    if node_str[0] == '-':
        var_node = ASTVariableNode(Symbols.VARIABLE, node_str[1:])
        node = ASTUnaryNode(Symbols.NOT)
        node.children = [var_node]
    elif node_str == "0":
        return None
    else:
        node = ASTVariableNode(Symbols.VARIABLE, node_str)
    return node

def read_dimacs(formula: str):
    conjunction = ASTNaryNode(Symbols.AND)
    for line in formula.split('\n'):
        if len(line) == 0:
            continue
        symbols = line.strip().split()
        if symbols[0] == "c":
            # comments with variable names
            continue

        if symbols[0] in ["0", "%"]:
            continue

        if symbols[0] == "p":
            if len(symbols) != 4:
                raise RuntimeError(f"Unexpected comment line: {line}")
            expected_vars = int(symbols[2])
            expected_clauses = int(symbols[3])
            continue

        if len(symbols) == 2:
            node = create_variable_node(symbols[0])
            conjunction.children.append(node)
            continue

        disjunction = ASTNaryNode(Symbols.OR)
        for symbol in symbols:
            node = create_variable_node(symbol)
            if node is not None:
                disjunction.children.append(node)
        conjunction.children.append(disjunction)
    
    log_node_info(conjunction)
    logger.info(f"EXPECTED: 'variables': {expected_vars}, 'subformulas': {expected_clauses}")
    return conjunction


def create_parser():
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str, help="Input file in DIMACS (.cnf) or in SMTLIB (.sat) format.")
    parser.add_argument("--output_to_stdout", action="store_true")
    return parser

def read_tree(input_file):
    extension = recognize_file_extension(input_file)
    formula = read_formula(input_file)
    if extension == Extensions.SMTLIB:
        return tseitin_encoding(formula, nnf_reduce_implications=True)
    elif extension == Extensions.DIMACS:
        return read_dimacs(formula)

def print_model(model, input_file, output_to_stdout):
    extension = recognize_file_extension(input_file)
    array_to_write = []
    if extension == Extensions.DIMACS:
        for variable, value in model.items():
            int_var = int(variable)
            if not value:
                int_var *= -1
            array_to_write.append(int_var)
        array_to_write = sorted(array_to_write, key=abs)
        for i in array_to_write:
            logger.info(i)
            if output_to_stdout:
                print(i)
    else:
        array_to_write = sorted(list(model.items()))
        for variable, value in array_to_write:
            if "__spec__" not in variable:
                logger.info(f"{variable}: {value}")
                if output_to_stdout:
                    print(f"{variable}: {value}")

def print_result(result, model, ndecs, nunit, time, input_file, output_to_stdout):
    if result == "SAT":
        logger.warning(f"SAT; decs: {ndecs}; unit: {nunit}; time: {time}")
        print_model(model, input_file, output_to_stdout)
    else:
        logger.warning(f"UNSAT; decs: {ndecs}; unit: {nunit}; time: {time}")

def get_info():
    return {
        "name": "DPPL",
        "taskName": "TASK 2",
        "benchmarkable": True
    }

def pack_result_to_dict(
    *,
    result,
    model,
    ndecs,
    nunit,
    time
):
    return {
        "result": result,
        "model": model,
        "number_of_decisions": ndecs,
        "number_of_unit_props": nunit,
        "time": time
    }

def find_model(
    *,
    input_file=None,
    warning=False,
    debug=False,
    output_to_stdout=False
):
    if input_file is None:
        return None
    set_debug_level(warning=warning, debug=debug)
    ast_tree_root = read_tree(input_file)
    start = timer()
    result, model, ndecs, nunit = dpll(ast_tree_root)
    end = timer()
    print_result(result, model, ndecs, nunit, end - start, input_file, output_to_stdout)
    return pack_result_to_dict(
        result=result,
        model=model,
        ndecs=ndecs,
        nunit=nunit,
        time=end - start
    )

if __name__ == "__main__":
    parser = create_parser()
    add_parser_debug_levels(parser)
    args = parser.parse_args()
    find_model(
        input_file=args.input_file,
        warning=args.warning,
        debug=args.debug,
        output_to_stdout=args.output_to_stdout
    )