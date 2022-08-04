
if [ $( docker ps -a | grep pgadmin-satsolver | wc -l ) -gt 0 ]; then
  docker restart pgadmin-satsolver
else
  docker run --name pgadmin-satsolver -e "PGADMIN_DEFAULT_EMAIL=name@example.com" -e "PGADMIN_DEFAULT_PASSWORD=admin" -p 5050:80 -d dpage/pgadmin4
fi
