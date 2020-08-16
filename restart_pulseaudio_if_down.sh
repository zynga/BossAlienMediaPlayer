#!/bin/bash

PULSEAUDIO_EXITCODE=$(bash -c 'pulseaudio --check -v > /dev/null 2>&1; echo $?')

if [[ $PULSEAUDIO_EXITCODE != 0 ]]; then
    echo "Restarting pulse audio"
    pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon
else
    echo "Pulse audio is running, no need to restart"
fi