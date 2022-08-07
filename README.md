# Programming Tasks for NAIL094 - Decision Procedures And Verification

### Run release in docker container

1. Start containers: `docker compose up -d --force-recreate --build`
  - the frontend runs at `http://localhost:5000`
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
- DPLL can be either ran as `python3 satsolver/task2.py <input_file>` or by using frontend

### Results
- I first implemented DPLL in May 2022. I faced problems with running benchmarks and comparing results, so I spent a month (probably too much time) developping a frontend so that I could store all the results in a database, access them, dynamically create graphs etc. Then I rewrote DPLL in August 2022, so that no advanced data structures (red-black trees/hash tables in python implementation of `dict` and `set`) would be used, just python `list`, and no copying would occur. The results can be seen in [whole comparison](./results/dpll.cmp.01.02.png) and [time comparison](./results/dpll.cmp.01.02.time.png), or in numerical data in [.csv](./results/dpll.cmp.01.02.csv). Basically we can see approximatelly 5-times improvement in speed, while dropping _pure literal elimination_ so further improvement should be possible. (The reason for not including _PLE_ is that I want the differences between _unit propagation_ with _adjacency lists_ and with _watched literals_ to be more visible).
- I tested the implementation on random sat benchmarks and on graph coloring problems from [cs.ubc benchmark page](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html). From the results it can be clearly seen that as the number of clauses and variables progresses the tasks become increasingly harder to solve with benchmark `uuf100-430` being the hardest. As expected proving satisfiability is easier than proving unsatisfiability.
----------------------

## Task 3: Watched Literals
- [executaable](satsolver/task3.py)
- [sources](satsolver/watched_literals/)
- Watched Literals can be either ran as `python3 satsolver/task3.py <input_file>` or by using frontend

### Results
- Assumption: Since the literal is watched only in a subset of all the clauses where it is present, I expected the number of checked clauses to be lower than in adjacency lists.
  - Result: In [the results graph (checked units)](results/dpll.wl.cmp.checked_units.png) we can see that it is the case with number of checked clauses halved compared to the same statistics when using adjacency lists.
- Assumption: Since I use pretty ingenious implementation of adjacency lists (instead of traversing the clauses to find out whether they are unit, I keep 2 stats, `clause.n_satisfied` and `clause.n_unsatisfied`), I expected the average times of execution to be similar.
  - Result: In [the results graph (time)](results/dpll.wl.cmp.time.png) we can see that the average times of execution actually got worse by about 10% in all the cases. I assume that it is because while in `adjacency lists` I initialize all the data-structures in the beginning, in `watched literals` I update the lists of clauses where the literal is watched with operations `.append`. Therefore I assume that the extra memory allocation worsens the results.
- To conclude, `watched literals` allow us to search through lower number of clauses when looking for unit and conflicting clauses. However a more clever implementation would be needed to beat `adjacency lists` when no `non-chronological` backtracking is used.

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
- [publishing docker images to docker repositories](https://docs.docker.com/docker-hub/repos/#pushing-a-docker-container-image-to-docker-hub)
- [publishing docker images with github actions](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)

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
