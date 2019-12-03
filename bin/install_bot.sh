#!/bin/sh
SERVER=https://kinto.dev.mozaws.net/v1

# Delete the bot first to start clean
curl -X DELETE ${SERVER}/accounts/cfr-bot -u cfr-bot:botpass

curl -v -X PUT ${SERVER}/accounts/cfr-bot \
     -d '{"data": {"password": "botpass"}}' \
     -H 'Content-Type:application/json'

