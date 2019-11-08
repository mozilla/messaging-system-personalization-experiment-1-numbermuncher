#!/bin/sh
CID=cfr-experiment-20191108
SERVER=http://localhost:8888/v1/
BASIC_AUTH=admin:s3cr3t

curl -X PUT ${SERVER}/buckets/main/collections/${CID} \
     -H 'Content-Type:application/json' \
     -u ${BASIC_AUTH}

#  curl -X POST ${SERVER}/buckets/main/collections/${CID}/records \
#       -d '{"data": {"title": "example"}}' \
#       -H 'Content-Type:application/json' \
#       -u ${BASIC_AUTH}
