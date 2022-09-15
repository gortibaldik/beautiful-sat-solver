# Task 4: CDCL
- [executable](../satsolver/task4.py)
- [sources](../satsolver/cdcl/)
### How to run
- CDCL pure `python3 -m satsolver.task4 <input_file>`
- CDCL with clause deletion `python3 -m satsolver.task4 --conflict_limit_deletion <how many conflicts till deletion> <input_file>`
- CDCL with restarts and clause deletion `python3 -m satsolver.task4 --conflict_limit_deletion <how many conflicts till deletion> --conflict_limit_restarts <how many conflicts till restart> <input_file>`
- or by using frontend

## Results
- Assumption: By using clause learning, the search space should be prunned, so with reasonably fast implementation, the execution time should be a lot lower
  - Result: The time reduction is of factor of more than 4. On [time comparison picture](../results/cdcl.wl.cmp.time.png) we can see huge differences in the runtime of CDCL and the fastest yet implementation, _watched literals iterative_. Regarding [comparisons of decision variables](../results/cdcl.wl.cmp.decs.png) and [comparisons of number of variables derived by unit propagations](../results/cdcl.wl.cmp.up.png) we can conclude that the search space is effectively prunned and that's the result for lower runtime.
- Assumption: By using restarts and clause deletion, we should be able to exploit learned clauses better and gain even better runtime
  - Setup: The restarts occur each time, the number of conflicts breaks the bareer of `conflict_limit`, which increases by a factor of `1.1`. On every restart each clause with _Lateral Block Distance_ bigger than `lbd_limit` is deleted, the `lbd_limit` increases by a factor of `1.1`. The initial values are 200 for `conflict_limit` and `3` for the `lbd_limit`.
  - Result: On [the time comparison picture](../results/cdcl.restarts.cmp.time.png) we can see that these settings of restarts slightly help. I may try some further finetuning of the values to gain even better results, however now I'm satisfied with even little improvement when using restarts.

__UPDATE__:
  - Since the results of geometrically increasing `conflict_limit` and `lbd_limit` weren't persuasive I spent some time reading about _luby_ which is the SotA. After implementing _luby_ I can conclude that this strategy helps a lot (lowering the runtime by more than 40% on the hardest problems). One particularity which is kind of puzzling for me is that I achieved the best results when I didn't increase `lbd_limit` by any factor. Hence the best results are for constant `lbd_limit` = 4. [The results picture](../results/cdcl.restarts.luby.cmp.png)

__UPDATE 2__:
  - After few more experiments I found out that what I have been referring to as _clause deletion and restarts_ was in reality only _clause deletion_ because of a bug in the code. After resolving the bug I'm not able to achieve better results with restarts than with only _clause deletion_. I cannot answer why it is so. I tried implementing some sort of basic heuristic (number of clauses where the literal is present at the moment of the restart is the criterion), but while lowering the runtime by a factor of 3, I still suffer that _restarts_ seem to hurt more than help. [New restarts comparison](../results/cdcl.restarts.02.png)
  