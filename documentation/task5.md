# Task 5: Decision Heuristics
- [executable (no restarts)](../satsolver/task5.py)
- [sources](../satsolver/decision_heuristics/)
### How to run
- CDCL pure `python3 -m satsolver.task5 <input_file>`
- or by using frontend

## Results
- Assumption:With VSIDS I should be able to improve on my best yet heuristic (Static Sum - `score[var] = sum(1 for clause in clauses if var in clause)`)
  - Result: It seems VSIDS isn't the best heuristic for this particular set of benchmarks. From my experiments and from profiling it looks like the number of checked unit clauses correlates strongly with the time of execution. From [the comparison of checked unit clauses between VSIDS and Static Sum](../results/vsids.cmp.checked.png) it looks like VSIDS heuristics causes much more checks than the simple Static Sum heuristic, which causes that [in the time comparison](../results/vsids.cmp.time.png) the VSIDS guided cdcl is about 50% worse.


- Regarding the assumptions, I have chosen the method of using the assumption as decision variable together with its negativity (assumption is in form of a literal). They work, I'm considering to use them for n-queens problem as kind of a reduction experiment: e.g. create nxn formula for huge n and then use assumptions to find the solution of n-queens problem for smaller n.
- Regarding random heuristic, it should have been the slowest one, and as can be seen in the [time comparison](../results/random.cmp.png) it is definitely the slowest one. (by a factor of 3) From the [time comparison with watched literals](../results/random.cmp.wl.png) it looks like random heuristics hurts the cdcl back to the level of dpll with watched literals.
