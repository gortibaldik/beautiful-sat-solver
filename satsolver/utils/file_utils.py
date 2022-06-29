import sys

from logzero import logger

def read_formula(input_file):
    formula = ""
    if input_file is None:
        formula = sys.stdin.read()
    else:
        with open(input_file, 'r') as f:
            formula = f.read()
    logger.debug(f"read formula: {formula}")
    return formula