import logzero
import sys
from argparse import ArgumentParser
from logzero import logger
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode
from satsolver.tseitin_encoding.parsing_utils import create_abstract_syntax_tree
from satsolver.tseitin_encoding.tseitin_transformation import turn_nnf_to_tseitin

def transform_to_numbers(tseitin_ast_tree_root: ASTAbstractNode, mapping):
    subformulas = []
    for sf in tseitin_ast_tree_root.children:
        string_repre = str(sf)
        tokens = string_repre.split()
        new_tokens = []
        negate = False
        for tk in tokens:
            if tk == "(" or tk == ")" or tk == "V":
                continue
            elif tk == "NOT":
                negate = True
            elif negate:
                new_tokens.append( -1 * mapping[tk])
                negate = False
            else:
                new_tokens.append(mapping[tk])
        set_tokens = set(new_tokens)
        should_be_printed = True
        for s in set_tokens:
            if -s in set_tokens:
                should_be_printed = False
                break
        if should_be_printed:
            subformulas.append(new_tokens)
    return subformulas

def get_sorting_item(x: str):
    if "__spec__" in x:
        val = x.split("__spec__")[1]
        return (1, int(val))
    return (0, x)

def _print_to_dmacs(tseitin_ast_tree_root: ASTAbstractNode, file):
    count_stats = tseitin_ast_tree_root.count()
    variables = sorted(list(count_stats["variables"]), key=get_sorting_item)
    mapping = {}
    for i, var in enumerate(variables):
        mapping[var] = i + 1
        if i == len(variables) - 1:
            print(f"c MAIN {i + 1} {var}", file=file)
        else:
            print(f"c {i + 1} {var}", file=file)

    subformulas = transform_to_numbers(tseitin_ast_tree_root, mapping)

    # len(subformulas) + 1 because we add special __spec__n variable as a separate clause
    print(f"p cnf {len(count_stats['variables'])} {len(subformulas)}", file=file)
    for sf in subformulas:
        print(" ".join([str(tk) for tk in sf]) + " 0", file=file)

def print_to_dmacs(tseitin_ast_tree_root: ASTAbstractNode, file):
    if file is not None:
        with open(file, 'w') as f:
            _print_to_dmacs(tseitin_ast_tree_root, f)
    else:
        _print_to_dmacs(tseitin_ast_tree_root, None)

def tseitin_encoding(formula: str, nnf_reduce_implications: bool):
    ast_tree_root = create_abstract_syntax_tree(formula)
    tseitin_ast_tree_root = turn_nnf_to_tseitin(ast_tree_root, nnf_reduce_implications)

    return tseitin_ast_tree_root

def create_parser():
    parser = ArgumentParser("Accepts input formula in NNF in SMT-LIB format and transforms it to Tseitin encoding in DIMACS format")
    parser.add_argument('input', nargs='?', default=None, type=str)
    parser.add_argument('output', nargs='?', default=None, type=str)
    parser.add_argument('--only_left_to_right', action='store_true', help="If specified, the input should be in NNF, and only left to right implications are used")
    return parser

def add_parser_debug_levels(parser: ArgumentParser):
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--warning', action='store_true')


def read_formula(input_file):
    formula = ""
    if input_file is None:
        formula = sys.stdin.read()
    else:
        with open(input_file, 'r') as f:
            formula = f.read()
    logger.debug(f"read formula: {formula}")
    return formula

def set_debug_level(args):
    if args.warning:
        logzero.loglevel(logzero.WARNING)
    elif args.debug:
        logzero.loglevel(logzero.DEBUG)
    else:
        logzero.loglevel(logzero.INFO)

def main():
    parser = create_parser()
    add_parser_debug_levels(parser)
    args = parser.parse_args()

    set_debug_level(args)
    formula = read_formula(args.input)
    tseitin_ast_tree_root = tseitin_encoding(formula, nnf_reduce_implications=args.only_left_to_right)
    print_to_dmacs(tseitin_ast_tree_root, args.output)

if __name__ == "__main__":
    main()