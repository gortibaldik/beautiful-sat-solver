import logzero
import sys

from argparse import ArgumentParser
from logzero import logger


def read_dimacs(formula: str, assignment):
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
            continue

        at_least_one = False
        for symbol in symbols:
            if symbol in assignment:
                at_least_one = True
        if not at_least_one:
            raise RuntimeError(f"Invalid assignment UNSAT: {line}")

def read_assignment(file):
    assignment = set()
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            assignment.add(line)
    return assignment

def create_parser():
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("assignment_file")
    return parser

# ----
# duplicated code from task1 because of relative import errors in python
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

def add_parser_debug_levels(parser: ArgumentParser):
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--warning', action='store_true')
# ----

def main():
    parser = create_parser()
    add_parser_debug_levels(parser)
    args = parser.parse_args()
    set_debug_level(args)
    assignment = read_assignment(args.assignment_file)
    formula = read_formula(args.input_file)
    read_dimacs(formula, assignment)
    logger.warning("OK")

if __name__ == "__main__":
    main()