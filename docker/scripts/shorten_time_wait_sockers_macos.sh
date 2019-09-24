#!/bin/bash
# See http://scratching.psybermonkey.net/2011/01/freebsd-how-to-reduce-timewait.html
sudo sysctl net.inet.tcp.msl=2500
