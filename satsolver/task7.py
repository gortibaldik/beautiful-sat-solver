from dataclasses import dataclass
import os
import satsolver.utils.general_setup as general_setup
from argparse import ArgumentParser
from logzero import logger
from pathlib import Path
from server.config import Config

SUDOKU_PROBLEM_NAME="sudoku"

def get_info(argumentParser: ArgumentParser=None):
  return general_setup.get_info(
    name="sudoku",
    taskName="TASK 7",
    benchmarkable=False
  )

def generate_sudoku_dimacs():
  pass

def main():
  parser = ArgumentParser()
  parser.add_argument("file_with_encoded_sudoku", help="File with sudoku (columns divided by space, rows divided by newline)")
  args = parser.parse_args()


if __name__ == "__main__":
  main()