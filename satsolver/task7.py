from dataclasses import dataclass
from functools import reduce
import os
from typing import List
from satsolver.task6 import CaV, exactly_one
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

def transform_sudoku(sudoku: str):
  sudoku_array = []
  for ir, row in enumerate(sudoku.strip().split('\n')):
    r = []
    for ic, col in enumerate(row.strip().split()):
      if col == "_":
        r.append(0)
        continue
      
      orcol = col
      try:
        col = int(col)
      except:
        col = 0
      if col not in range(1, 10):
        raise RuntimeError(f"Invalid sudoku: {sudoku} ({ir + 1}, {ic + 1}) == {orcol}")
      
      r.append(col)
    sudoku_array.append(r)
  return sudoku_array

def row_col_n_to_ix(ir, ic, val):
  if val in range(1, 10):
    return ir * 81 + ic * 9 + val
  raise RuntimeError(f"val needs to be in range [1, 9] ({val})")

def unit_clauses(sudoku: List[List[int]], cav: CaV):
  s = ""
  for ir, row in enumerate(sudoku):
    for ic, val in enumerate(row):
      if val != 0:
        cav.c += 1
        s += f"{row_col_n_to_ix(ir, ic, val)} 0" + "\n"
  return s

def exactly_one_in_each_cell(sudoku: List[List[int]], cav: CaV):
  s = ""
  for ir, row in enumerate(sudoku):
    for ic, val in enumerate(row):
      if val == 0:
        s += exactly_one([row_col_n_to_ix(ir, ic, v) for v in range(1, 10)], cav)
  return s

def exactly_one_in_each_row(cav: CaV):
  s = ""
  for ir in range(9):
    for v in range(1, 10):
      s += exactly_one([row_col_n_to_ix(ir, ic, v) for ic in range(9)], cav)
  return s

def exactly_one_in_each_col(cav: CaV):
  s = ""
  for ic in range(9):
    for v in range(1, 10):
      s += exactly_one([row_col_n_to_ix(ir, ic, v) for ir in range(9)], cav)
  
  return s

def exactly_one_in_each_unit(cav: CaV):
  s = ""
  adds = []
  for i in range(9):
    adds.append((i // 3, i % 3))
  for iur in range(0, 9, 3):
    for iuc in range(0, 9, 3):
      for v in range(1, 10):
        s += exactly_one([row_col_n_to_ix(iur + ar, iuc + ac, v) for ar, ac in adds], cav)
  
  return s

def _generate_sudoku_dimacs(sudoku: List[List[int]]):
  cav = CaV()
  s = ""
  s += unit_clauses(sudoku, cav)
  s += exactly_one_in_each_cell(sudoku, cav)
  s += exactly_one_in_each_row(cav)
  s += exactly_one_in_each_col(cav)
  s += exactly_one_in_each_unit(cav)
  s = f"p cnf {9 * 9 * 9} {cav.c}" + "\n" + s
  return s

def generate_sudoku_dimacs(
  sudoku:str,
  generate_new=False,
  **kwargs
):
  sudoku_array = transform_sudoku(sudoku)
  sudoku_str = ''.join(map(str, reduce(lambda x, y: x + y, sudoku_array)))
  filename = f"sudoku.{sudoku_str}.cnf"

  benchmark_folder = os.path.join(
    Config.SATSMT_BENCHMARK_ROOT,
    SUDOKU_PROBLEM_NAME
  )
  Path(benchmark_folder).mkdir(parents=True, exist_ok=True)
  filename = os.path.join(
    benchmark_folder,
    filename
  )
  if os.path.isfile(filename):
    return filename
  
  if not generate_new:
    return None
  
  with open(filename, 'w') as f:
    s = _generate_sudoku_dimacs(sudoku_array)
    f.write(s)
  logger.warning(f"Generated new nqueens file: {filename}")
  return filename

def main():
  parser = ArgumentParser()
  parser.add_argument("file_with_encoded_sudoku", help="File with sudoku (columns divided by space, rows divided by newline)")
  args = parser.parse_args()


if __name__ == "__main__":
  main()