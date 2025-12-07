#!/bin/bash

echo "==== DB TEST ===="
curl -i http://localhost:8000/db-test-c

echo -e "
==== LIST MATCHES ===="
curl -i http://localhost:8000/matches

echo -e "
==== LIST OFFERS ===="
curl -i http://localhost:8000/offers

echo -e "
==== CREATE OFFER ===="
curl -i -X POST http://localhost:8000/offers     -H "Content-Type: application/json"     -d '{
        "matchId": "123",
        "recipientId": "abcde",
        "status": "pending"
    }'

echo -e "
==== PAGINATION + ETAG ===="
curl -i "http://localhost:8000/offers?limit=5&offset=0"

echo -e "
==== TEST ETAG ===="
etag=$(curl -sI http://localhost:8000/offers | grep ETag | awk '{print $2}')
echo "ETag: $etag"
curl -i -H "If-None-Match: $etag" http://localhost:8000/offers

echo -e "
==== TRIGGER MATCH ===="
curl -i -X POST http://localhost:8000/do-match

echo -e "
==== DONORS (MS1) ===="
curl -i http://localhost:8000/donors

echo -e "
==== ORGANS (MS1) ===="
curl -i http://localhost:8000/organs

echo -e "
==== RECIPIENTS (MS2) ===="
curl -i http://localhost:8000/recipients

echo -e "
==== NEEDS (MS2) ===="
curl -i http://localhost:8000/needs

echo -e "
==== TEST DUPLICATE MATCH INSERT ===="
curl -i -X POST http://localhost:8000/matches     -H "Content-Type: application/json"     -d '{"donorId":"1","recipientId":"1"}'

echo -e "
==== TEST DUPLICATE OFFER INSERT ===="
curl -i -X POST http://localhost:8000/offers     -H "Content-Type: application/json"     -d '{"matchId":"1","status":"pending"}'

echo -e "
==== DONE ===="
