# SAT-Solver
- this is a python implementation of the most known sat-solving approaches
- there is also a server-client app to make the satsolver-benchmarking as easy as possible
- as 2 little side-projects the app contains sat-reductions of sudoku and n-queens problems, easily runnable with the frontend, with nice visualizations

## Run Release in Docker Container

1. Start containers: `docker compose up -d --force-recreate --build`
  - the frontend runs at `http://localhost:5000`
  - __log levels__: `DEBUG`: everything; `INFO`: transformation of the formula to cnf, model of the formula, sat/unsat; `WARNING`: only sat/unsat
2. Stop containers: `docker compose stop`

3. (Only if you had had any of previous versions installed) Rebuild: `docker compose build --no-cache --pull`

-----

## Reference Information

- this project was developped as a part of exam for course NAIL094 - Decision Procedures and Verification at Charles University in Prague
- the implementation consisted of fulfilling a set of tasks

### Tasks

1. [Task 1: Tseitin Encoding and DIMACS format](documentation/task1.md)
2. [Task 2: DPLL](documentation/task2.md)
3. [Task 3: Watched Literals](documentation/task3.md)
4. [Task 4: CDCL](documentation/task4.md)
5. [Task 5: Decision Heuristics](documentation/task5.md)
6. [Task 6: N-Queens](documentation/task6.md)
7. [Task 7: Sudoku](documentation/task7.md)

------

### [Resources](documentation/resources.md)

- interesting web pages with information that helped me with developing the sat-solver and the server-client architecture

### [Setup Information](documentation/run.md)

- information about development-setup, release creation, and other information which is helpful if you want to help with development of the app
