#!/bin/bash

echo Starting Development LDAP
echo Use this set up only for local development.
echo Browse http://localhost:44304 to get into LDAP admin.
echo Log in with user \"cn=admin,dc=example,dc=org\", password \"admin\".
echo Copy admin object to create more users as needed.
echo Use the following settings in mopidy.conf.secrets:
echo "LDAP_URI ldap://host.docker.internal:389"
echo "LDAP_SCHEMA CN=#USER_NAME#,DC=example,DC=org"

docker-compose -f ./docker/ldap-docker-compose.yml up
