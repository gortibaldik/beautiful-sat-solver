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

- select problem parameters (e.g. number of queens)

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
![nqueens_stats](./frontend_nqueens_stats.png)
