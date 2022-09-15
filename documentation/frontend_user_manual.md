# Frontend User Manual

## Main Screen

![main_screen](./frontend_benchmarks.png)

- here you can choose an algorithm and a benchmark on which the algorithm will be ran
- a set of statistics will be collected to enable comparison of the algorithm
- each algorithm is in its own card
- you can select:
  - the benchmark
  - log level for the log information that the algorithm will produce on the benchmark
  - parameters which affect the properties of the algorithm

![main_screen_algo](./frontend_benchmarks_algo.png)

-----

## Results Screen

![results_screen](./frontend_results.png)

- allows for browsing the already ran benchmarks as well as data visualizations

#### Select Benchmarks for Visualizations
![results_screen_select](./frontend_results_select.png)

#### Show Cumulative Visualization
![results_screen_cumulative](./frontend_results_cumulative.png)

#### Show Individual Statistics
![results_screen_statistics](./frontend_results_stats.png)

-----
## N-Queens Problem Screen

![nqueens_screen](./frontend_nqueens_select.png)

- select:
  - problem parameters (e.g. number of queens)
  - algorithm parameters

#### Show Results

- shows:
  - DIMACS encoding of the problem
  - logs of the algorithm
  - visualization of the placement of queens on the chessboard

![nqueens_results](./frontend_nqueens_results.png)

#### Benchmark Run

- if you check the checkbox `run_as_benchmark` then the algorithm will be ran successively for N=3,4,... until the time of the run won't cross the `timeout` parameter
- after the run, you can browse to `NQueens-Results` page, where the benchmark can be visualized in the same way as in the `Results` page

![nqueens_benchmark](./frontend_nqueens_benchmark.png)

#### Visualization

![nqueens_stats](./frontend_nqueens_stats.png)

------

## Sudoku Screen

- the sudoku screen allows:
  - typing out the sudoku in the following format:
    - columns are separated by a space
    - rows are separated by a newline
    - blank symbol: `_`
    - only numbers are supported
  - generating the sudoku:
    - by pressing `Generate Sudoku` button
    - selection of the difficulty of the sudoku by selecting from `difficulty` dropdown

![sudoku_screen](./frontend_sudoku.png)

#### Generated Sudoku

- the generated sudoku is displayed
- light bleu is used for cells with blanks

![sudoku_generated](./frontend_sudoku_generate.png)

#### Sudoku Results

- shows:
  - DIMACS encoding of the problem
  - logs of the algorithm
  - filled sudoku, with filled numbers in light bleu cells

![sudoku_results](./frontend_sudoku_results.png)
