#!/bin/bash
# for macOS
watch -n 30 "(date; ./count_connections.sh) | tee -a ~/connections.log"
