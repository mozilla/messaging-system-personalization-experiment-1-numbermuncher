#!/bin/sh
SERVER=https://kinto.dev.mozaws.net/v1
curl -v -X PUT ${SERVER}/accounts/devuser \
     -d '{"data": {"password": "devpass"}}' \
     -H 'Content-Type:application/json'
