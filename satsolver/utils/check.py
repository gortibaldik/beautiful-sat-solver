import logzero
import sys

from argparse import ArgumentParser
from logzero import logger
from satsolver.utils.file_utils import read_formula
from satsolver.utils.logging_utils import set_debug_level
from satsolver.utils.parser_utils import add_parser_debug_levels


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
            raise RuntimeError("Invalid assignment UNSAT: \n\tformula:{}\n\tassignment:{}".format(line, assignment))

def read_assignment(file):
    assignment = set()
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            parts = line.split(":")
            if len(parts) == 1:
                assignment.add(line)
            elif len(parts) == 2:
                assignment_true = parts[1].strip() == "True"
                if assignment_true:
                    assignment.add(parts[0])
    return assignment

def create_parser():
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("assignment_file")
    return parser

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