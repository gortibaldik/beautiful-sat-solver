# Task 2: DPLL
- [executable](../satsolver/task2.py)
- [sources](../satsolver/dpll/)
- DPLL can be either ran as `python3 -m satsolver.task2 <input_file>` or by using frontend


## Results
- I first implemented DPLL in May 2022. I faced problems with running benchmarks and comparing results, so I spent a month (probably too much time) developping a frontend so that I could store all the results in a database, access them, dynamically create graphs etc. Then I rewrote DPLL in August 2022, so that no advanced data structures (red-black trees/hash tables in python implementation of `dict` and `set`) would be used, just python `list`, and no copying would occur. The results can be seen in [whole comparison](.././results/dpll.cmp.01.02.png) and [time comparison](.././results/dpll.cmp.01.02.time.png), or in numerical data in [.csv](.././results/dpll.cmp.01.02.csv). Basically we can see approximatelly 5-times improvement in speed, while dropping _pure literal elimination_ so further improvement should be possible. (The reason for not including _PLE_ is that I want the differences between _unit propagation_ with _adjacency lists_ and with _watched literals_ to be more visible).
- I tested the implementation on random sat benchmarks and on graph coloring problems from [cs.ubc benchmark page](../https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html). From the results it can be clearly seen that as the number of clauses and variables progresses the tasks become increasingly harder to solve with benchmark `uuf100-430` being the hardest. As expected proving satisfiability is easier than proving unsatisfiability.
