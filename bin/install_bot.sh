#!/bin/sh
SERVER=https://kinto.dev.mozaws.net/v1

# Delete the bot first to start clean
curl -X DELETE ${SERVER}/accounts/devuser -u devuser:devpass

curl -v -X PUT ${SERVER}/accounts/devuser \
     -d '{"data": {"password": "devpass"}}' \
     -H 'Content-Type:application/json'

