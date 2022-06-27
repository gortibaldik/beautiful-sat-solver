# create volume if it doesn't exist yet
if [ ! $( docker volume ls | grep satsolver_volume | wc -l ) -gt 0 ]; then
  echo "Creating docker volume: satsolver_volume"
  docker volume create satsolver_volume
fi

if [ $( docker ps -a | grep postgres-satsolver | wc -l ) -gt 0 ]; then
  docker restart postgres-satsolver
else
  echo "Creating and running new container!"
  docker run -d --name postgres-satsolver -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=satsolverdb -v satsolver_volume:/var/lib/postgresql/data postgres:latest
fi
