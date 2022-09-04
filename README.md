# Programming Tasks for NAIL094 - Decision Procedures And Verification

### Run release in docker container

1. Start containers: `docker compose up -d --force-recreate --build`
  - the frontend runs at `http://localhost:5000`
  - __log levels__: `DEBUG`: everything; `INFO`: transformation of the formula to cnf, model of the formula, sat/unsat; `WARNING`: only sat/unsat
2. Stop containers: `docker compose stop`

3. (Only if you had had any of previous versions installed) Rebuild: `docker compose build --no-cache --pull`


-------------------

## Task 1: Tseitin Encoding and DIMACS format
- [executable](satsolver/task1.py)
- [sources](satsolver/tseitin_encoding/)

----------------------

## Task 2: DPLL
- [executable](satsolver/task2.py)
- [sources](satsolver/dpll/)
- DPLL can be either ran as `python3 -m satsolver.task2 <input_file>` or by using frontend

### Results
- I first implemented DPLL in May 2022. I faced problems with running benchmarks and comparing results, so I spent a month (probably too much time) developping a frontend so that I could store all the results in a database, access them, dynamically create graphs etc. Then I rewrote DPLL in August 2022, so that no advanced data structures (red-black trees/hash tables in python implementation of `dict` and `set`) would be used, just python `list`, and no copying would occur. The results can be seen in [whole comparison](./results/dpll.cmp.01.02.png) and [time comparison](./results/dpll.cmp.01.02.time.png), or in numerical data in [.csv](./results/dpll.cmp.01.02.csv). Basically we can see approximatelly 5-times improvement in speed, while dropping _pure literal elimination_ so further improvement should be possible. (The reason for not including _PLE_ is that I want the differences between _unit propagation_ with _adjacency lists_ and with _watched literals_ to be more visible).
- I tested the implementation on random sat benchmarks and on graph coloring problems from [cs.ubc benchmark page](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html). From the results it can be clearly seen that as the number of clauses and variables progresses the tasks become increasingly harder to solve with benchmark `uuf100-430` being the hardest. As expected proving satisfiability is easier than proving unsatisfiability.
----------------------

## Task 3: Watched Literals
- [executable](satsolver/task3.py)
- [sources](satsolver/watched_literals/)
- Watched Literals can be either ran as `python3 -m satsolver.task3 <input_file>` or by using frontend

### Results
- Assumption: Since the literal is watched only in a subset of all the clauses where it is present, I expected the number of checked clauses to be lower than in adjacency lists.
  - Result: In [the results graph (checked units)](results/dpll.wl.cmp.checked_units.png) we can see that it is the case with number of checked clauses halved compared to the same statistics when using adjacency lists.
- Assumption: Since I use pretty ingenious implementation of adjacency lists (instead of traversing the clauses to find out whether they are unit, I keep 2 stats, `clause.n_satisfied` and `clause.n_unsatisfied`), I expected the average times of execution to be similar.
  - Result: In [the results graph (time)](results/dpll.wl.cmp.time.png) we can see that the average times of execution actually got worse by about 10% in all the cases. I assume that it is because while in `adjacency lists` I initialize all the data-structures in the beginning, in `watched literals` I update the lists of clauses where the literal is watched with operations `.append`. Therefore I assume that the extra memory allocation worsens the results.
- To conclude, `watched literals` allow us to search through lower number of clauses when looking for unit and conflicting clauses. However a more clever implementation would be needed to beat `adjacency lists` when no `non-chronological` backtracking is used.
- __UPDATE__: I implemented new encoding of literals and variables, and also an iterative solution. It seems like iterative dpll.v5 is the best yet, however the time of execution varies greatly, hence I'm not quite sure about [the results](./results/dpll.wl.cmp.02.csv).
- __UPDATE 2__: I spent another day optimizing the watched literals implementation and now [the results](./results/dpll.wl.cmp.03.csv) correspond more or less to my assumptions. Now, the watched literals are by far the fastest method (as can be seen in [this graph](./results/dpll.wl.cmp.time.02.png)). As I have found out the reason for slowness of my implementation was two-fold. 1. At first I used classes instead of simple numbers/array indices to represent literals and variables. 2. When I implemented better encoding, I still suffered from a lot of function calls manipulating with these numbers. As I have inlined most of them, the watched literals got faster by about 35%.

-----

## Task 4: CDCL
- [executable (no restarts)](satsolver/task4.py)
- [sources](satsolver/cdcl/)
#### How to run
- CDCL pure `python3 -m satsolver.task4 <input_file>`
- CDCL with clause deletion `python3 -m satsolver.task4 --conflict_limit_deletion <how many conflicts till deletion> <input_file>`
- CDCL with restarts and clause deletion `python3 -m satsolver.task4 --conflict_limit_deletion <how many conflicts till deletion> --conflict_limit_restarts <how many conflicts till restart> <input_file>`
- or by using frontend

### Results
- Assumption: By using clause learning, the search space should be prunned, so with reasonably fast implementation, the execution time should be a lot lower
  - Result: The time reduction is of factor of more than 4. On [time comparison picture](results/cdcl.wl.cmp.time.png) we can see huge differences in the runtime of CDCL and the fastest yet implementation, _watched literals iterative_. Regarding [comparisons of decision variables](results/cdcl.wl.cmp.decs.png) and [comparisons of number of variables derived by unit propagations](results/cdcl.wl.cmp.up.png) we can conclude that the search space is effectively prunned and that's the result for lower runtime.
- Assumption: By using restarts and clause deletion, we should be able to exploit learned clauses better and gain even better runtime
  - Setup: The restarts occur each time, the number of conflicts breaks the bareer of `conflict_limit`, which increases by a factor of `1.1`. On every restart each clause with _Lateral Block Distance_ bigger than `lbd_limit` is deleted, the `lbd_limit` increases by a factor of `1.1`. The initial values are 200 for `conflict_limit` and `3` for the `lbd_limit`.
  - Result: On [the time comparison picture](results/cdcl.restarts.cmp.time.png) we can see that these settings of restarts slightly help. I may try some further finetuning of the values to gain even better results, however now I'm satisfied with even little improvement when using restarts.

__UPDATE__:
  - Since the results of geometrically increasing `conflict_limit` and `lbd_limit` weren't persuasive I spent some time reading about _luby_ which is the SotA. After implementing _luby_ I can conclude that this strategy helps a lot (lowering the runtime by more than 40% on the hardest problems). One particularity which is kind of puzzling for me is that I achieved the best results when I didn't increase `lbd_limit` by any factor. Hence the best results are for constant `lbd_limit` = 4. [The results picture](results/cdcl.restarts.luby.cmp.png)

__UPDATE 2__:
  - After few more experiments I found out that what I have been referring to as _clause deletion and restarts_ was in reality only _clause deletion_ because of a bug in the code. After resolving the bug I'm not able to achieve better results with restarts than with only _clause deletion_. I cannot answer why it is so. I tried implementing some sort of basic heuristic (number of clauses where the literal is present at the moment of the restart is the criterion), but while lowering the runtime by a factor of 3, I still suffer that _restarts_ seem to hurt more than help. [New restarts comparison](results/cdcl.restarts.02.png) 

-----

## Task 5: Decision Heuristics
- [executable (no restarts)](satsolver/task5.py)
- [sources](satsolver/decision_heuristics/)
#### How to run
- CDCL pure `python3 -m satsolver.task5 <input_file>`
- or by using frontend

### Results
- Assumption:With VSIDS I should be able to improve on my best yet heuristic (Static Sum - `score[var] = sum(1 for clause in clauses if var in clause)`)
  - Result: It seems VSIDS isn't the best heuristic for this particular set of benchmarks. From my experiments and from profiling it looks like the number of checked unit clauses correlates strongly with the time of execution. From [the comparison of checked unit clauses between VSIDS and Static Sum](results/vsids.cmp.checked.png) it looks like VSIDS heuristics causes much more checks than the simple Static Sum heuristic, which causes that [in the time comparison](results/vsids.cmp.time.png) the VSIDS guided cdcl is about 50% worse.


- Regarding the assumptions, I have chosen the method of using the assumption as decision variable together with its negativity (assumption is in form of a literal). They work, I'm considering to use them for n-queens problem as kind of a reduction experiment: e.g. create nxn formula for huge n and then use assumptions to find the solution of n-queens problem for smaller n.
- Regarding random heuristic, it should have been the slowest one, and as can be seen in the [time comparison](results/random.cmp.png) it is definitely the slowest one. (by a factor of 3) From the [time comparison with watched literals](results/random.cmp.wl.png) it looks like random heuristics hurts the cdcl back to the level of dpll with watched literals.

------

## Task 6: N-Queens
- [executable](satsolver/task6.py)
- create a file with the encoded n-queens problem, then use any of the satsolvers to actually run it
- or use frontend

### Results
- I implemented two new features into the frontend, visualization of the placement of queens, and database with visualization for comparison
- I ran the following experiment:

  1. set up timeout
  2. run the problem for all the `n` until single solution takes longer than `timeout`

- As expected, DPLL is the weakest, reaching the timeout at N == 18, watched literals improve to N == 20, cdcl improves to N == 22 ([results](results/nqueens.my_impl.png))
- I also ran several other satsolvers on the benchmark. Each of them surpased my implementation of cdcl by a huge margin, namely: Glucose ended at N == 64, Minisat at N == 67 ([results](results/nqueens.others.png))

-------

# Task 7: Sudoku
- [sudoku generator](server/views/sudoku/sudoku-generator/sudoku_generator.py)
- creates a valid sudoku with unique solution, cloned from https://github.com/RutledgePaulV/sudoku-generator

### Flow of execution CLI

1. Generate sudoku: `python3 -m server.views.sudoku.sudoku_generator.sudoku_generator <difficulty> > sudoku.file`
2. Encode sudoku to cnf: `python3 -m satsolver.task7 --sudoku_file sudoku.file`
  - the result is saved to `sudoku.cnf`
  - the filename is settable with `--output-file` argument
3. Solve the sudoku: `python3 -m satsolver.other_solvers sudoku.cnf --solver_name Glucose`

### Results

- The generated sudoku should have an unique solution, which should be inferrable without any guessing (without search, just by logical assumptions)
- Hence even the hardest instances should be solvable just by unit propagation, which is indeed true for all the solvers that I have implemented.
- However it is not the case for Glucose and Minisat which for whatever reason decide exactly 2 variables and then infer everything else by unit propagation
- This behavior isn't observable in neither Lingeling nor Cadical.

#### Resources

- [How to deploy flask with vue.js in docker container](https://testdriven.io/blog/deploying-flask-to-heroku-with-docker-and-gitlab/)
- [Proxy pass in nginx](https://dev.to/danielkun/nginx-everything-about-proxypass-2ona)
- [Develop SPA with Flask and Vue.js](https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/)
- [WSGI servers](https://www.fullstackpython.com/wsgi-servers.html)
- [What is Green Unicorn](https://vsupalov.com/what-is-gunicorn/)
- [Using fetch API](https://flaviocopes.com/fetch-api/)
- [Redis Message Queue for long running tasks](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxii-background-jobs)
- [official Docker tutorial - Docker compose part](https://docs.docker.com/get-started/08_using_compose/)
- [better selectors for tables](https://mdbootstrap.com/education/bootstrap/admin-dashboard-lesson-6/)
- [sql alchemy 1](https://realpython.com/python-sqlite-sqlalchemy/#working-with-sqlalchemy-and-python-objects)
- [sql alchemy 2](https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/)
- [sql alchemy 3](https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application)
- [sql alchemy 4](https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/)
- [postgres connection string](https://stackoverflow.com/questions/3582552/what-is-the-format-for-the-postgresql-connection-string-url)
- [postgres pooling](https://stackoverflow.blog/2020/10/14/improve-database-performance-with-connection-pooling/)
- [publishing docker images to docker repositories](https://docs.docker.com/docker-hub/repos/#pushing-a-docker-container-image-to-docker-hub)
- [publishing docker images with github actions](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
- [simple satsolver implementation](https://sahandsaba.com/understanding-sat-by-implementing-a-simple-sat-solver-in-python.html)
- [cdcl 1](https://cse442-17f.github.io/Conflict-Driven-Clause-Learning/)
- [cdcl - handbook on satisfiability](https://www.ics.uci.edu/~dechter/courses/ics-275a/winter-2016/readings/SATHandbook-CDCL.pdf)
- [cdcl - some python implementation](https://github.com/z11i/pysat)
- [cdcl - presentation on the topic](http://ssa-school-2016.it.uu.se/wp-content/uploads/2016/06/LaurentSimon.pdf)
- [glucose cdcl solver](https://www.ijcai.org/Proceedings/09/Papers/074.pdf)
- [ipynb with various sat improvements](https://github.com/aimacode/aima-python/blob/master/improving_sat_algorithms.ipynb)

#### Problems with installation of `psycopg2`

- [stack overflow](https://stackoverflow.com/questions/19843945/psycopg-python-h-no-such-file-or-directory)

#### Run development server for both frontend and backend in docker container

1. Start containers:`scripts/start_docker_dev.sh`
2. Stop containers: `scripts/stop_docker_dev.sh`

#### Database checks on dev:

- You can connect to `pg-admin` at `localhost:5050` and connect to the database (`hostname=satdb`, `username=postgres`, `password=admin`)

#### How to prepare new release of frontend image

- `scripts/build_frontend.sh` - build frontend as `satsolver_frontend_base`
- `docker tag satsolver_frontend_base gortibaldik/satsolver_frontend_base:<version>`
- `docker push gortibaldik/satsolver_frontend_base:<version>`
