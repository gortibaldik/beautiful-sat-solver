echo "db ip address: \"$DB_IP_ADDRESS\""

CAN_CONNECT=1
while [ $CAN_CONNECT -ne 0 ]; do
  flask db current 2> /dev/null
  CAN_CONNECT=$?
  echo "LAST RETURN CODE: \"$CAN_CONNECT\""
done

[ ! -d "$DB_MIGRATIONS_DIR" ] && echo "Initializing migrations folder" && (flask db init || exit)

flask db migrate -m "$MIGRATION_NAME"

# if the migration isn't applied to the database yet, then apply it
(flask db current | grep "(head)" && echo "migration is applied") || flask db upgrade