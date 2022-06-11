scripts/start_redis.sh

export REDIS_QUEUE_NAME="satsmt_background_worker_queue"
export SATSMT_RESULT_LOGS="result_logs"
export SATSMT_BENCHMARK_ROOT="benchmarks/"
export BENCHMARKED_RESULTS_AVAILABILITY="35000"
echo "redis queue name: \"$REDIS_QUEUE_NAME\""
rq worker ${REDIS_QUEUE_NAME} > rq_log_file 2> rq_error_log_file &
rq_worker_job_id=$!

python3 -m server.app

# clean up
kill $rq_worker_job_id
scripts/stop_redis.sh
