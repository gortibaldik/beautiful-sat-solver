# Task 6: N-Queens
- [executable](../satsolver/task6.py)
- create a file with the encoded n-queens problem, then use any of the satsolvers to actually run it
- or use frontend

## Results
- I implemented two new features into the frontend, visualization of the placement of queens, and database with visualization for comparison
- I ran the following experiment:

  1. set up timeout
  2. run the problem for all the `n` until single solution takes longer than `timeout`

- As expected, DPLL is the weakest, reaching the timeout at N == 18, watched literals improve to N == 20, cdcl improves to N == 22 ([results](../results/nqueens.my_impl.png))
- I also ran several other satsolvers on the benchmark. Each of them surpased my implementation of cdcl by a huge margin, namely: Glucose ended at N == 64, Minisat at N == 67 ([results](../results/nqueens.others.png))
