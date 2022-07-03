FROM base_image:latest as production
WORKDIR /app
COPY ./server/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./server ./server
COPY ./satsolver ./satsolver
 
CMD gunicorn -b 0.0.0.0:5000 server:app --daemon --access-logfile accessLogfile --error-logfile errorLogfile && \
    sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
    nginx -g 'daemon off;'
