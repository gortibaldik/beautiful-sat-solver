# start REDIS
if [ $( docker ps -a | grep redis-stack-server | wc -l ) -gt 0 ]; then
  docker restart redis-stack-server
else
  docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack:latest
fi

export REDIS_QUEUE_NAME="satsmt_background_worker_queue"
export SATSMT_RESULT_LOGS="result_logs"
export SATSMT_BENCHMARK_ROOT="benchmarks/"
export BENCHMARKED_RESULTS_AVAILABILITY="35000"
echo "redis queue name: \"$REDIS_QUEUE_NAME\""
rq worker ${REDIS_QUEUE_NAME} > rq_log_file 2> rq_error_log_file &
rq_worker_job_id=$!

python3 -m server.app
kill $rq_worker_job_id