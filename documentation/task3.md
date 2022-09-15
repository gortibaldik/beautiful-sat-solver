# Task 3: Watched Literals
- [executable](../satsolver/task3.py)
- [sources](../satsolver/watched_literals/)
- Watched Literals can be either ran as `python3 -m satsolver.task3 <input_file>` or by using frontend

## Results
- Assumption: Since the literal is watched only in a subset of all the clauses where it is present, I expected the number of checked clauses to be lower than in adjacency lists.
  - Result: In [the results graph (checked units)](../results/dpll.wl.cmp.checked_units.png) we can see that it is the case with number of checked clauses halved compared to the same statistics when using adjacency lists.
- Assumption: Since I use pretty ingenious implementation of adjacency lists (instead of traversing the clauses to find out whether they are unit, I keep 2 stats, `clause.n_satisfied` and `clause.n_unsatisfied`), I expected the average times of execution to be similar.
  - Result: In [the results graph (time)](../results/dpll.wl.cmp.time.png) we can see that the average times of execution actually got worse by about 10% in all the cases. I assume that it is because while in `adjacency lists` I initialize all the data-structures in the beginning, in `watched literals` I update the lists of clauses where the literal is watched with operations `.append`. Therefore I assume that the extra memory allocation worsens the results.
- To conclude, `watched literals` allow us to search through lower number of clauses when looking for unit and conflicting clauses. However a more clever implementation would be needed to beat `adjacency lists` when no `non-chronological` backtracking is used.
- __UPDATE__: I implemented new encoding of literals and variables, and also an iterative solution. It seems like iterative dpll.v5 is the best yet, however the time of execution varies greatly, hence I'm not quite sure about [the results](.././results/dpll.wl.cmp.02.csv).
- __UPDATE 2__: I spent another day optimizing the watched literals implementation and now [the results](.././results/dpll.wl.cmp.03.csv) correspond more or less to my assumptions. Now, the watched literals are by far the fastest method (as can be seen in [this graph](.././results/dpll.wl.cmp.time.02.png)). As I have found out the reason for slowness of my implementation was two-fold. 1. At first I used classes instead of simple numbers/array indices to represent literals and variables. 2. When I implemented better encoding, I still suffered from a lot of function calls manipulating with these numbers. As I have inlined most of them, the watched literals got faster by about 35%.
