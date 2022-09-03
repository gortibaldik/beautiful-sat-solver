from dataclasses import dataclass
import os
import satsolver.utils.general_setup as general_setup
from argparse import ArgumentParser
from logzero import logger
from pathlib import Path
from server.config import Config

def get_info(argumentParser: ArgumentParser=None):
  return general_setup.get_info(
    name="nqueens",
    taskName="TASK 6",
    benchmarkable=False
  )

@dataclass
class CaV:
  c: int = 0
  v: int = 0

def at_least_one(rng, cav: CaV):
  s = ""
  for i in rng:
    if len(s) == 0:
      s = str(i)
    else:
      s += f" {i}"
  s += " 0 \n"
  cav.c += 1
  return s

def at_most_one(rng, cav: CaV):
  s = ""
  for i in range(len(rng)):
    for j in range(i + 1, len(rng)):
      s += f"-{rng[i]} -{rng[j]} 0" + "\n"
      cav.c += 1
  return s

def exactly_one(rng, cav):
  s = at_least_one(rng, cav)
  s += at_most_one(rng, cav)
  return s

def row_col_to_ix(row, col, n):
  return row * n + col + 1

def column_constraints(n, cav):
  s = ""
  for c in range(n):
    s += exactly_one([row_col_to_ix(r, c, n) for r in range(n)], cav)
  return s

def row_constraints(n, cav):
  s = ""
  for r in range(n):
    s += exactly_one([row_col_to_ix(r, c, n) for c in range(n)], cav)
  return s

def positive_diagonals(n, cav):
  s = ""
  for start in range(n - 1):
    s += at_most_one([row_col_to_ix(r + start, r, n) for r in range(n - start)], cav)
    if start != 0:
      s += at_most_one([row_col_to_ix(r, r + start, n) for r in range(n - start)], cav)
  return s

def negative_diagonals(n, cav):
  s = ""
  for start in range(n - 1):
    s += at_most_one([row_col_to_ix(r, n - r - start - 1, n) for r in range(n - start)], cav)
    if start != 0:
      s += at_most_one([row_col_to_ix(r + start, n - r - 1, n) for r in range(n - start)], cav)
  return s

def _generate_nqueens_dimacs(n):
  cav = CaV()
  s = ""
  s += row_constraints(n, cav)
  s += column_constraints(n, cav)
  s += positive_diagonals(n, cav)
  s += negative_diagonals(n, cav)
  s = f"p cnf {n * n} {cav.c}" + "\n" + s
  return s

NQUEENS_PROBLEM_NAME="nqueens"

def generate_nqueens_dimacs(n, generate_new=True):
  if n < 0:
    raise RuntimeError(f"N cannot be negative: N == {n}")
  benchmark_folder = os.path.join(
    Config.SATSMT_BENCHMARK_ROOT,
    NQUEENS_PROBLEM_NAME
  )
  Path(benchmark_folder).mkdir(parents=True, exist_ok=True)
  filename = os.path.join(
    benchmark_folder,
    f"{n}.cnf"
  )
  if os.path.isfile(filename):
    return filename
  
  if not generate_new:
    return None
  
  with open(filename, 'w') as f:
    s = _generate_nqueens_dimacs(n)
    f.write(s)
  logger.warning(f"Generated new nqueens file: {filename}")
  return filename

def main():
  parser = ArgumentParser()
  parser.add_argument("n", help="Number of queens")
  args = parser.parse_args()
  generate_nqueens_dimacs(args.n)

if __name__ == "__main__":
  main()