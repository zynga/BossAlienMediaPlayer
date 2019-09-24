#/bin/bash

docker exec `docker ps -qaf "name=production_nginx"` tail -f /var/log/nginx/access.alt.log
