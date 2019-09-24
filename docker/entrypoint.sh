#!/bin/bash

(cd /var/lib/mopidy/mopidy_bamp && sudo python setup.py develop && cd -)

mopidy local scan

exec "$@"
