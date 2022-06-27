scripts/start_redis.sh
scripts/start_postgres.sh

export REDIS_QUEUE_NAME="satsmt_background_worker_queue"
export DB_IP_ADDRESS="$(scripts/get_ip_address_of_docker_postgres.sh)"
export DB_MIGRATIONS_DIR="server/migrations"
echo "redis queue name: \"$REDIS_QUEUE_NAME\""
echo "db ip address: \"$DB_IP_ADDRESS\""
echo "db migrations dir: \"$DB_MIGRATIONS_DIR\""

[ ! -d "rq_logs" ] && mkdir rq_logs

rq worker ${REDIS_QUEUE_NAME} > "rq_logs/rq_log_file" 2> "rq_logs/rq_error_log_file" &

export FLASK_APP="server:app"
python3 -m server.before_app
flask run

# clean up
scripts/stop_postgres.sh
scripts/stop_redis.sh
