FROM base_image:latest as production
WORKDIR /app
COPY --from=frontend_base_image:latest /app/dist /usr/share/nginx/html
COPY ./server/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./server ./server
COPY ./satsolver ./satsolver
 
CMD python -m server.before_app && \
    gunicorn -b 0.0.0.0:5000 server:app --daemon --access-logfile accessLogfile --error-logfile errorLogfile && \
    sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
    nginx -g 'daemon off;'
