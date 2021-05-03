#/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SERVER_NAME=$1
AWS_CREDENTIALS=~/.aws/credentials
# Check NGINX_CONTAINER is named after the nginx container defined in docker-compose-prod-base.yml
NGINX_CONTAINER=production_nginx

if [ -z "$1" ]; then
    echo Please specify the domain you want to renew
    exit 1
fi

echo Make sure your AWS credentials at $AWS_CREDENTIALS are up to date

docker run -it --rm --name certbot \
    -v "$DIR/letsencrypt/etc/:/etc/letsencrypt/" \
    -v "$DIR/letsencrypt/varlib/:/var/lib/letsencrypt/" \
    -v "$AWS_CREDENTIALS:/root/.aws/credentials" \
    certbot/dns-route53 certonly \
        --dns-route53 \
        -d "$SERVER_NAME"

DOCKER_OK=$?

# If certificate was renewed and nginx is running, send a signal to restart web server
if [ $DOCKER_OK ] && [ "$( docker container inspect -f '{{.State.Running}}' $NGINX_CONTAINER )" == "true" ]; then
    echo Reloading nginx at container $NGINX_CONTAINER
    docker exec $NGINX_CONTAINER service nginx reload
fi


