CAN_CONNECT=1
while [ $CAN_CONNECT -ne 0 ]; do
  flask db current 2> /dev/null
  CAN_CONNECT=$?
  echo "LAST RETURN CODE: \"$CAN_CONNECT\""
done

python -m server.before_app || exit
sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf
nginx
sleep 10

echo "STARTING FLASK!"
flask run