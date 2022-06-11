if [ $( docker ps -a | grep redis-stack-server | wc -l ) -gt 0 ]; then
  docker restart redis-stack-server
else
  docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack:latest
fi
