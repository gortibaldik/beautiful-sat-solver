# Programming Tasks for NAIL094 - Decision Procedures And Verification

## Task 1: Tseitin Encoding and DIMACS format
- [executable](task1.py)
- [sources](tseitin_encoding/)

## Task 2: DPLL
- [executable](task2.py)
- [sources](dpll/)

### Results
- the DPLL solver was run on [randomly selected](dpll/task2_filter.py) tenth of all the examples from each test split (e.g on tenth of `uf50-218`, on tenth of `uuf50-218` etc.), with the exception of 100-430 where it was a 1 / 100th of the test set
- reported times are averages over all the runs
- I stopped the experiment on 100 variables, 430 clauses test set, because of too high computational requirements

#### SAT

| Test set  | Time  | Unit Propagated Variables | Decision Variables |
|-----------|-------|---------------------------|--------------------|
| uf20-91   | 0.01  | 24.3                      | 9.5                |
| uf50-218  | 0.16  | 210.9                     | 82.9               |
| uf75-325  | 0.39  | 380.4                     | 130.2              |
| uf100-430 | 13.59 | 10 843.4                  | 3 687.6            |

#### UNSAT

| Test set   | Time  | Unit Propagated Variables | Decision Variables |
|------------|-------|---------------------------|--------------------|
| uff50-218  | 0.42  | 428.3                     | 190.9              |
| uff75-325  | 3.36  | 2 814.0                   | 1076.0             |
| uff100-430 | 39.98 | 27 209.3                  | 10 294.0           |
