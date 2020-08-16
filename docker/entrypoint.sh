#!/bin/bash

(cd /var/lib/mopidy/mopidy_bamp && sudo python3 setup.py develop && cd -)

mopidy local scan

exec "$@"
