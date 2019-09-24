#!/bin/bash

netstat -nat | awk '{print $6}' | sort | uniq -c | sort -n
