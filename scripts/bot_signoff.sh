#!/bin/sh

# Create a cfr-bot with a dummy password for local testing
SERVER=http://localhost:8888/v1

curl -X PUT ${SERVER}/accounts/cfr-bot \
     -d '{"data": {"password": "botpass"}}' \
     -H 'Content-Type:application/json'

BASIC_AUTH=cfr-bot:botpass

# Create 3 collections
# * main/cfr-models
# * main/cfr-experiment
# * main/cfr-control

curl -X PUT ${SERVER}/buckets/main/collections/cfr-models \
     -H 'Content-Type:application/json' \
     -u ${BASIC_AUTH}

curl -X PUT ${SERVER}/buckets/main/collections/cfr-experiment \
     -H 'Content-Type:application/json' \
     -u ${BASIC_AUTH}

curl -X PUT ${SERVER}/buckets/main/collections/cfr-control \
     -H 'Content-Type:application/json' \
     -u ${BASIC_AUTH}

# Add the bot to editor role for 3 collections:
# * main/cfr-models
# * main/cfr-experiment
# * main/cfr-control

curl -X PATCH $SERVER/buckets/main/groups/cfr-models-editors \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}

curl -X PATCH $SERVER/buckets/main/groups/cfr-experiment-editors \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}

curl -X PATCH $SERVER/buckets/main/groups/cfr-control-editors \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}

# Add the bot to reviewer role for 3 collections:
# * main/cfr-models
# * main/cfr-experiment
# * main/cfr-control

curl -X PATCH $SERVER/buckets/main/groups/cfr-models-reviewers \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}
curl -X PATCH $SERVER/buckets/main/groups/cfr-experiment-reviewers \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}
curl -X PATCH $SERVER/buckets/main/groups/cfr-control-reviewers \
     -H 'Content-Type:application/json-patch+json' \
     -d '[{ "op": "add", "path": "/data/members/0", "value": "account:cfr-bot" }]' \
     -u ${BASIC_AUTH}

# Generate some dummy data in the cfr-models bucket

curl -X PUT ${SERVER}/buckets/main/collections/cfr-models/records/cfr-models \
         -H 'Content-Type:application/json' \
         -d "{\"data\": {\"property\": 321.1}}" \
         -u ${BASIC_AUTH} --verbose
