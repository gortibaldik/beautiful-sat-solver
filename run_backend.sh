scripts/start_redis.sh

export REDIS_QUEUE_NAME="satsmt_background_worker_queue"
export SATSMT_RESULT_LOGS="result_logs"
export SATSMT_BENCHMARK_ROOT="benchmarks/"
export BENCHMARKED_RESULTS_AVAILABILITY="35000"
echo "redis queue name: \"$REDIS_QUEUE_NAME\""
rq worker ${REDIS_QUEUE_NAME} > rq_log_file 2> rq_error_log_file &

export FLASK_APP=app.py
flask run

# clean up
scripts/stop_redis.sh
