#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SERVER_NAME=bamp.yourdomainhere.com

if [ "$SERVER_NAME" == "bamp.yourdomainhere.com" ]; then
	echo "Replace SERVER_NAME with the domain you will use for BAMP before running this script"
	exit 6
fi

echo "Starting BAMP on $SERVER_NAME"

if [ ! -d $DIR/letsencrypt/etc/live/$SERVER_NAME ]; then
    echo "You do not have the SSL certificates to run $SERVER_NAME, please install them before continuing"
	exit 5
fi

# if arg provided use as ip address
if [ -z "$1" ]
then
	MY_IP=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`
	if [ `echo "$MY_IP" | wc -l` -gt 1 ]
	then
		echo "You seem to have multiple IP addresses:"
		echo $MY_IP
		echo "please run $0 <MY_IP>"
		exit 3
	fi
else
	MY_IP=$1
fi

./restart_pulseaudio_if_down.sh

echo "Updating config for IP: $MY_IP"

echo "Updating docker-compose.yml"
CMD="sed 's|PULSE_SERVER=.*|PULSE_SERVER=$MY_IP|g' $DIR/docker/docker-compose-prod-base.yml > $DIR/docker/docker-compose.yml"
eval $CMD

echo "Updating nginx.conf"
CMD="sed 's|SERVER_NAME|$SERVER_NAME|g' $DIR/docker/nginx-base.conf > $DIR/docker/nginx.conf"
eval $CMD

echo "Injecting secrets into mopidy.conf"

if [ ! -f $DIR/docker/mopidy.conf.secrets ]; then
    echo "Cannot find mopidy.conf.secrets, please create this file with the secrets seen in mopidy.conf"
	exit 4
fi

cp $DIR/docker/mopidy-base.conf $DIR/docker/mopidy.conf

while read LINE
do
    SECRET_NAME="$( echo $LINE | cut -f1 -d' ' )"
    SECRET_VALUE="$( echo $LINE | cut -f2 -d' ' )"
    CMD="sed 's|$SECRET_NAME|$SECRET_VALUE|g' $DIR/docker/mopidy.conf > $DIR/docker/mopidy.conf.tmp"
    eval $CMD
    mv $DIR/docker/mopidy.conf.tmp $DIR/docker/mopidy.conf
done < $DIR/docker/mopidy.conf.secrets

BUILD_HASH="$(tar -cf - $DIR 2> /dev/null | md5)"
echo Build hash is $BUILD_HASH
CMD="sed 's|BUILD_HASH|$BUILD_HASH|g' $DIR/docker/mopidy.conf > $DIR/docker/mopidy.conf.tmp"
eval $CMD
mv $DIR/docker/mopidy.conf.tmp $DIR/docker/mopidy.conf

(cd $DIR/docker && \
	docker-compose -f $DIR/docker/docker-compose.yml up --build && \
	cd -)

