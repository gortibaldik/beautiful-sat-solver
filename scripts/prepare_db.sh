migration_name="$1"

scripts/start_postgres.sh

export FLASK_APP="server:app"
export DB_IP_ADDRESS="$(scripts/get_ip_address_of_docker_postgres.sh)"
export DB_MIGRATIONS_DIR="server/database/migrations"
echo "db ip address: \"$DB_IP_ADDRESS\""

[ ! -d "$DB_MIGRATIONS_DIR" ] && echo "Initializing migrations folder" && (flask db init || exit)

flask db migrate -m "$migration_name" || exit

# if the migration isn't applied to the database yet, then apply it
(flask db current | grep "(head)" && echo "migration is applied") || flask db upgrade

scripts/stop_postgres.sh