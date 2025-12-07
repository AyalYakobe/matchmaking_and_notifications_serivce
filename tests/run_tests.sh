#!/bin/bash

BASE_URL="https://matchmaking-service-549668844609.us-central1.run.app"

echo "==== DB TEST ===="
curl -i $BASE_URL/db-test-c


echo -e "\n==== LIST MATCHES ===="
curl -i $BASE_URL/internal/matches


echo -e "\n==== GET FULL MATCH (example ID=1) ===="
curl -i $BASE_URL/matches/1/full


echo -e "\n==== LIST OFFERS ===="
curl -i $BASE_URL/offers


echo -e "\n==== CREATE OFFER ===="
curl -i -X POST $BASE_URL/offers \
  -H "Content-Type: application/json" \
  -d '{
        "matchId": "123",
        "recipientId": "abcde",
        "status": "pending"
      }'


echo -e "\n==== PAGINATION + ETAG ===="
curl -i "$BASE_URL/offers?limit=5&offset=0"


echo -e "\n==== TEST ETAG ===="
etag=$(curl -sI $BASE_URL/offers | grep -i ETag | awk '{print $2}' | tr -d '\r')
echo "ETag: $etag"
curl -i -H "If-None-Match: $etag" $BASE_URL/offers


echo -e "\n==== TRIGGER MATCH ===="
curl -i -X POST $BASE_URL/match/do-match


echo -e "\n==== MS1 DONORS ===="
curl -i $BASE_URL/ms1/donors


echo -e "\n==== MS1 ORGANS ===="
curl -i $BASE_URL/ms1/organs


echo -e "\n==== MS2 RECIPIENTS ===="
curl -i $BASE_URL/ms2/recipients


echo -e "\n==== MS2 NEEDS ===="
curl -i $BASE_URL/ms2/needs


echo -e "\n==== DONE ===="