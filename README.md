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

### Run development server for both frontend and backend

1. Run flask backend server:
2. Run npm frontend dev server: `./run_frontend.sh`

### Run in docker container

1. Build docker container: `docker build -t satsmt:latest .`
2. Run docker container: `docker run -d --name satsmt-container -e "PORT=8765" -p 8007:8765 satsmt:latest`
3. When finished your experiments: `docker stop satsmt-container`
4. Remove container to be able to rebuild: `docker rm satsmt-container`

-----

#### Resources

- [How to deploy flask with vue.js in docker container](https://testdriven.io/blog/deploying-flask-to-heroku-with-docker-and-gitlab/)
- [Proxy pass in nginx](https://dev.to/danielkun/nginx-everything-about-proxypass-2ona)
- [Develop SPA with Flask and Vue.js](https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/)
- [WSGI servers](https://www.fullstackpython.com/wsgi-servers.html)
- [What is Green Unicorn](https://vsupalov.com/what-is-gunicorn/)
- [Using fetch API](https://flaviocopes.com/fetch-api/)
- [Redis Message Queue for long running tasks](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxii-background-jobs)
- [official Docker tutorial - Docker compose part](https://docs.docker.com/get-started/08_using_compose/)