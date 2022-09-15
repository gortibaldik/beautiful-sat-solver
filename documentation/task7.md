# Task 7: Sudoku
- [sudoku generator](../server/views/sudoku/sudoku-generator/sudoku_generator.py)
- creates a valid sudoku with unique solution, cloned from https://github.com/RutledgePaulV/sudoku-generator

## Flow of execution CLI

1. Generate sudoku: `python3 -m server.views.sudoku.sudoku_generator.sudoku_generator <difficulty> > sudoku.file`
2. Encode sudoku to cnf: `python3 -m satsolver.task7 --sudoku_file sudoku.file`
  - the result is saved to `sudoku.cnf`
  - the filename is settable with `--output-file` argument
3. Solve the sudoku: `python3 -m satsolver.other_solvers sudoku.cnf --solver_name Glucose`

## Results

- The generated sudoku should have an unique solution, which should be inferrable without any guessing (without search, just by logical assumptions)
- Hence even the hardest instances should be solvable just by unit propagation, which is indeed true for all the solvers that I have implemented.
- However it is not the case for Glucose and Minisat which for whatever reason decide exactly 2 variables and then infer everything else by unit propagation
- This behavior isn't observable in neither Lingeling nor Cadical.
