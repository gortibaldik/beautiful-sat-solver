scripts/start_redis.sh

export REDIS_QUEUE_NAME="satsmt_background_worker_queue"
echo "redis queue name: \"$REDIS_QUEUE_NAME\""

[ ! -d "rq_logs" ] && mkdir rq_logs

rq worker ${REDIS_QUEUE_NAME} > "rq_logs/rq_log_file" 2> "rq_logs/rq_error_log_file" &

export FLASK_APP=app.py
flask run

# clean up
scripts/stop_redis.sh
