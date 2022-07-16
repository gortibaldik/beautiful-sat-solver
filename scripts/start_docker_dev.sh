docker compose -f docker-compose.dev.yml --project-name satsolver_dev  build --no-cache
docker compose -f docker-compose.dev.yml --project-name satsolver_dev up -d --force-recreate
