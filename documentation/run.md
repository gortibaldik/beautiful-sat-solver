## Run development server for both frontend and backend in docker container

1. Start containers:`scripts/start_docker_dev.sh`
2. Stop containers: `scripts/stop_docker_dev.sh`

## Database checks on dev:

- You can connect to `pg-admin` at `localhost:5050` and connect to the database (`hostname=satdb`, `username=postgres`, `password=admin`)

## How to prepare new release of frontend image

- `scripts/build_frontend.sh` - build frontend as `satsolver_frontend_base`
- `docker tag satsolver_frontend_base gortibaldik/satsolver_frontend_base:<version>`
- `docker push gortibaldik/satsolver_frontend_base:<version>`
