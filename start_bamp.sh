#!/bin/bash

inject_value() { # $1 $LINE, $2 FILENAME
	local SECRET_NAME="$( echo $1 | cut -f1 -d' ' )"
    local SECRET_VALUE="$( echo $1 | cut -f2 -d' ' )"
    local CMD="sed 's|$SECRET_NAME|$SECRET_VALUE|g' $2 > $2.tmp"
    eval $CMD
    mv $2.tmp $2
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

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
CMD="sed 's|PULSE_SERVER=.*|PULSE_SERVER=$MY_IP|g' $DIR/docker/docker-compose-base.yml > $DIR/docker/docker-compose.yml"
eval $CMD

echo "Injecting secrets into mopidy.conf and icecast.xml"

if [ ! -f $DIR/docker/mopidy.conf.secrets ]; then
    echo "Cannot find mopidy.conf.secrets, please create this file with the secrets seen in mopidy.conf"
	exit 4
fi

cp $DIR/docker/mopidy-base.conf $DIR/docker/mopidy.conf
cp $DIR/docker/icecast/icecast-base.xml $DIR/docker/icecast/icecast.xml

while read LINE
do
	inject_value "$LINE" "$DIR/docker/mopidy.conf"
	inject_value "$LINE" "$DIR/docker/icecast/icecast.xml"
done < $DIR/docker/mopidy.conf.secrets

inject_value "USE_LDAP_STARTTLS false" "$DIR/docker/mopidy.conf"
inject_value "LDAP_CERTIFICATE_PATH None" "$DIR/docker/mopidy.conf"
inject_value "XHEADERS_ENABLED false" $DIR/docker/mopidy.conf
inject_value "ICECAST_URL http://$MY_IP:8000" $DIR/docker/mopidy.conf

BUILD_HASH="$(tar -cf - $DIR/mopidy_bamp/mopidy_bamp/static 2> /dev/null | md5sum)"
echo Build hash is $BUILD_HASH
inject_value "BUILD_HASH $BUILD_HASH" $DIR/docker/mopidy.conf

(cd $DIR && \
	docker-compose -f $DIR/docker/docker-compose.yml up --build && \
	cd -)

