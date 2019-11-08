#!/bin/sh
CID=cfr
SERVER=https://firefox.settings.services.mozilla.com/v1
curl ${SERVER}/buckets/main/collections/${CID}/records
