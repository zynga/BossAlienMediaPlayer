#!/bin/bash

docker ps -qa | xargs docker container rm -f
