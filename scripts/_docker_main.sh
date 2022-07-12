CAN_CONNECT=1
while [ $CAN_CONNECT -ne 0 ]; do
  flask db current #2> /dev/null
  CAN_CONNECT=$?
  echo "LAST RETURN CODE: \"$CAN_CONNECT\""
done

python -m server.before_app
sleep 10
gunicorn -b 0.0.0.0:5000 server:app --daemon --access-logfile accessLogfile --error-logfile errorLogfile
sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'