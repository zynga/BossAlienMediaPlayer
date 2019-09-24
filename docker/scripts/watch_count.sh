#!/bin/bash
# for the mopidy container
watch -n 30 "(date | tee -a /var/lib/mopidy/mopidy_bamp/netstat.log) && (netstat -nat | awk '{print \$6}' | sort | uniq -c | sort -n | tee -a /var/lib/mopidy/mopidy_bamp/netstat.log)"

watch -n 30 "netstat -nat | awk '{print \$6}' | sort | uniq -c | sort -n"
