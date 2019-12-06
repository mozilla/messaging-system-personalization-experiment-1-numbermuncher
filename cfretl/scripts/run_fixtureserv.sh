#!/bin/sh
SERVER=https://kinto.dev.mozaws.net/v1

while true
do
    # Create the bot first to start clean
    curl -v -X PUT ${SERVER}/accounts/devuser \
         -d '{"data": {"password": "devpass"}}' \
         -H 'Content-Type:application/json'
    python install_fixtures.py
    sleep 10
done
