#!/bin/bash
# for macOS
lsof -p $(pgrep vpnkit) | wc -l
