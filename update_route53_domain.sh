#!/bin/bash
# Usage: ./update_route53_domain.sh {IP of the domain}
# Make sure SERVER_NAME and HOSTED_ZONE_ID are correctly set
# and that AWS_CREDENTIALS are up to date
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# Must be a FQDN, include the dot at the end
SERVER_NAME=bamp.yourdomainhere.com.
HOSTED_ZONE_ID=HOSTEDZONEIDHERE
AWS_CREDENTIALS=~/.aws

# if arg provided use as ip address
if [ -z "$1" ]
then
	MY_IP=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`
	if [ `echo "$MY_IP" | wc -l` -gt 1 ]
	then
		echo "You seem to have multiple IP addresses:"
		echo $MY_IP
		echo "please run $0 <MY_IP>"
		exit 3
	fi
else
	MY_IP=$1
fi

echo Make sure your AWS credentials at $AWS_CREDENTIALS are up to date

TEMP_FILE=`mktemp`

tee ${TEMP_FILE} <<EOT
{
    "Comment": "UPSERT BAMP Domain",
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "${SERVER_NAME}",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "${MY_IP}"
                    }
                ]
            }
        }
    ]
}
EOT

TEMP_FILE_DIRNAME=`dirname ${TEMP_FILE}`
TEMP_FILE_BASENAME=`basename ${TEMP_FILE}`

docker run -v ${AWS_CREDENTIALS}:/root/.aws -v ${TEMP_FILE_DIRNAME}:/opt/files --rm -it public.ecr.aws/aws-cli/aws-cli route53 change-resource-record-sets --hosted-zone-id ${HOSTED_ZONE_ID} --change-batch file:///opt/files/${TEMP_FILE_BASENAME}
