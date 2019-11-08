#!/bin/sh

BASIC_AUTH=admin:s3cr3t
BUCKET_NAME=cfr-experiment-1

curl -X PUT ${SERVER}/buckets/${BUCKET_NAME} \
     -d '{"permissions": {"read": ["system.Everyone"], "collection:create": ["system.Authenticated"]}}' \
     -H 'Content-Type:application/json' \
     -u $BASIC_AUTH
