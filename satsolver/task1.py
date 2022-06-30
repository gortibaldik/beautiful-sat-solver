import logzero
import sys
from argparse import ArgumentParser
from logzero import logger
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode
from satsolver.tseitin_encoding.parsing_utils import create_abstract_syntax_tree
from satsolver.tseitin_encoding.tseitin_transformation import turn_nnf_to_tseitin
from satsolver.utils.file_utils import read_from_input
from satsolver.utils.logging_utils import set_debug_level
from satsolver.utils.parser_utils import add_parser_debug_levels

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

def print_or_save_to_content(line, file=None, content=None, should_be_printed=True):
    if should_be_printed:
        print(line, file=file)
    else:
        return content + line + "\n"

def _print_to_dmacs(tseitin_ast_tree_root: ASTAbstractNode, file, should_be_printed=True):
    count_stats = tseitin_ast_tree_root.count()
    variables = sorted(list(count_stats["variables"]), key=get_sorting_item)
    mapping = {}
    content = ""
    for i, var in enumerate(variables):
        mapping[var] = i + 1
        if i == len(variables) - 1:
            line = f"c MAIN {i + 1} {var}"
        else:
            line = f"c {i + 1} {var}"
        content = print_or_save_to_content(line, file, content, should_be_printed)

    subformulas = transform_to_numbers(tseitin_ast_tree_root, mapping)

    # len(subformulas) + 1 because we add special __spec__n variable as a separate clause
    line = f"p cnf {len(count_stats['variables'])} {len(subformulas)}"
    content = print_or_save_to_content(line, file, content, should_be_printed)
    for sf in subformulas:
        line = " ".join([str(tk) for tk in sf]) + " 0"
        content = print_or_save_to_content(line, file, content, should_be_printed)
    
    return content, mapping

def print_to_dmacs(tseitin_ast_tree_root: ASTAbstractNode, file=None, should_be_printed=True):
    if file is not None:
        with open(file, 'w') as f:
            content, mapping = _print_to_dmacs(tseitin_ast_tree_root, f)
    else:
        content, mapping = _print_to_dmacs(tseitin_ast_tree_root, None, should_be_printed=should_be_printed)
    return content, mapping

def tseitin_encoding(formula: str, nnf_reduce_implications: bool=False):
    ast_tree_root = create_abstract_syntax_tree(formula)
    tseitin_ast_tree_root = turn_nnf_to_tseitin(ast_tree_root, nnf_reduce_implications)

    return tseitin_ast_tree_root

def dimacs_tseitin_encoding(formula :str, nnf_reduce_implications=True):
    tseitin_ast_tree_root = tseitin_encoding(formula, nnf_reduce_implications=nnf_reduce_implications)
    return print_to_dmacs(tseitin_ast_tree_root, should_be_printed=False)

def create_parser():
    parser = ArgumentParser("Accepts input formula in NNF in SMT-LIB format and transforms it to Tseitin encoding in DIMACS format")
    parser.add_argument('input', nargs='?', default=None, type=str)
    parser.add_argument('output', nargs='?', default=None, type=str)
    parser.add_argument('--only_left_to_right', action='store_true', help="If specified, the input should be in NNF, and only left to right implications are used")
    return parser

def main():
    parser = create_parser()
    add_parser_debug_levels(parser)
    args = parser.parse_args()

    set_debug_level(warning=args.warning, deubg=args.debug)
    formula = read_from_input(args.input)
    tseitin_ast_tree_root = tseitin_encoding(formula, nnf_reduce_implications=args.only_left_to_right)
    print_to_dmacs(tseitin_ast_tree_root, args.output)

def get_info():
    return {
        "name": "Tseitin Encoding",
        "taskName": "TASK 1",
        "benchmarkable": False
    }

if __name__ == "__main__":
    main()