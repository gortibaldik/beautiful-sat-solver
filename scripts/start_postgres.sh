# create volume if it doesn't exist yet
if [ ! $( docker volume ls | grep satsolver_db_volume_dev | wc -l ) -gt 0 ]; then
  echo "Creating docker volume: satsolver_db_volume_dev"
  docker volume create satsolver_db_volume_dev
fi

if [ $( docker ps -a | grep satsolver_db_dev | wc -l ) -gt 0 ]; then
  docker restart satsolver_db_dev
else
  echo "Creating and running new container!"
  docker run -d --name satsolver_db_dev -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=satsolverdb -v satsolver_db_volume_dev:/var/lib/postgresql/data postgres:latest
fi
