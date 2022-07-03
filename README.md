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

### Run in docker container

1. Build the base image for the docker container `scripts/build_base_image.sh`
2. Build the infrastructure `docker-compose build --no-cache`
3. Start containers: `docker-compose up -d`

### Run development server for both frontend and backend

1. Initialize the database: `scripts/prepare_database.sh "initial_migration"`
2. In one terminal window: Run flask backend server and redis queue: `./run_backend.sh`
3. In another terminal window: Run npm frontend dev server: `./run_frontend.sh`

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
- [better selectors for tables](https://mdbootstrap.com/education/bootstrap/admin-dashboard-lesson-6/)
- [sql alchemy 1](https://realpython.com/python-sqlite-sqlalchemy/#working-with-sqlalchemy-and-python-objects)
- [sql alchemy 2](https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/)
- [sql alchemy 3](https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application)
- [sql alchemy 4](https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/)
- [postgres connection string](https://stackoverflow.com/questions/3582552/what-is-the-format-for-the-postgresql-connection-string-url)
- [postgres pooling](https://stackoverflow.blog/2020/10/14/improve-database-performance-with-connection-pooling/)

#### Problems with installation of `psycopg2`

- [stack overflow](https://stackoverflow.com/questions/19843945/psycopg-python-h-no-such-file-or-directory)
