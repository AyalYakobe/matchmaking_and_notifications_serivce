#!/bin/bash

BASE_URL="https://matchmaking-service-549668844609.us-central1.run.app"

echo "==== DB TEST ===="
curl -i $BASE_URL/db-test-c

echo -e "
==== LIST MATCHES ===="
curl -i $BASE_URL/matches

echo -e "
==== LIST OFFERS ===="
curl -i $BASE_URL/offers

echo -e "
==== CREATE OFFER ===="
curl -i -X POST $BASE_URL/offers \
  -H "Content-Type: application/json" \
  -d '{
        "matchId": "123",
        "recipientId": "abcde",
        "status": "pending"
      }'

echo -e "
==== PAGINATION + ETAG ===="
curl -i "$BASE_URL/offers?limit=5&offset=0"

echo -e "
==== TEST ETAG ===="
etag=$(curl -sI $BASE_URL/offers | grep -i ETag | awk '{print $2}' | tr -d '\r')
echo "ETag: $etag"
curl -i -H "If-None-Match: $etag" $BASE_URL/offers

echo -e "
==== TRIGGER MATCH ===="
curl -i -X POST $BASE_URL/do-match

echo -e "
==== DONORS (MS1) ===="
curl -i $BASE_URL/donors

echo -e "
==== ORGANS (MS1) ===="
curl -i $BASE_URL/organs

echo -e "
==== RECIPIENTS (MS2) ===="
curl -i $BASE_URL/recipients

echo -e "
==== NEEDS (MS2) ===="
curl -i $BASE_URL/needs

echo -e "
==== TEST DUPLICATE MATCH INSERT ===="
curl -i -X POST $BASE_URL/matches \
  -H "Content-Type: application/json" \
  -d '{"donorId":"1","recipientId":"1"}'

echo -e "
==== TEST DUPLICATE OFFER INSERT ===="
curl -i -X POST $BASE_URL/offers \
  -H "Content-Type: application/json" \
  -d '{"matchId":"1","status":"pending"}'

echo -e "
==== DONE ===="
