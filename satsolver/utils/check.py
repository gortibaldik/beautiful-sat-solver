from argparse import ArgumentParser
from logzero import logger
from satsolver.utils.file_utils import read_formula
from satsolver.utils.logging_utils import set_debug_level
from satsolver.utils.parser_utils import add_parser_debug_levels


def check_if_assignment_satisfies_formula(formula: str, assignment, is_satisfiable):
    if not is_satisfiable:
        if assignment is not None and len(assignment) != 0:
            raise RuntimeError("Invalid assignment SAT (expected UNSAT): \n\tformula: {}\n\tassignment: {}".format(formula.split('\n'), assignment))
        return
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
            raise RuntimeError("Invalid assignment UNSAT (expected SAT): \n\tformula:{}\n\tassignment:{}".format(line, assignment))

def read_assignment_from_file(file):
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

def read_assignment_from_model(model):
    assignment = set()
    for var, val in model.items():
        if val:
            assignment.add(var)
    return assignment

def check_assignment(
    *,
    input_file,
    assignment_source,
    warning=False,
    debug=False,
    read_from_file=True,
    is_satisfiable=True
):
    set_debug_level(warning=warning, debug=debug)
    if read_from_file:
        assignment = read_assignment_from_file(assignment_source)
    else:
        assignment = read_assignment_from_model(assignment_source)
    formula = read_formula(input_file)
    check_if_assignment_satisfies_formula(formula, assignment, is_satisfiable)
    logger.warning("OK")
    return True

def create_parser():
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("assignment_file")
    parser.add_argument("--unsat", action="store_true")
    return parser

def main():
    parser = create_parser()
    add_parser_debug_levels(parser)
    args = parser.parse_args()
    check_assignment(
        input_file=args.input_file,
        assignment_source=args.assignment_file,
        warning=args.warning,
        debug=args.debug,
        is_satisfiable=not args.unsat
    )

if __name__ == "__main__":
    main()