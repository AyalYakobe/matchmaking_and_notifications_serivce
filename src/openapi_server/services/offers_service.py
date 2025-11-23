# src/openapi_server/services/offers_service.py

import json
import hashlib
from fastapi import APIRouter, Response, HTTPException

from openapi_server.models.offer import Offer
from openapi_server.db.connection import get_connection

router = APIRouter()


# ---------------------------------------------------------
# GET /offers   (pagination + ETag + hypermedia)
# ---------------------------------------------------------
@router.get("/offers", response_model=list[Offer])
async def offers_get(limit: int = 10, offset: int = 0, response: Response = None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT
            id,
            match_id AS matchId,
            recipient_id AS recipientId,
            status,
            created_at AS createdAt,
            updated_at AS updatedAt
        FROM offers
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )
    rows = cur.fetchall()

    # Generate ETag
    body = json.dumps(rows, default=str)
    etag = hashlib.sha1(body.encode()).hexdigest()
    response.headers["ETag"] = etag

    # Pagination (next page link)
    response.headers["Link"] = (
        f'</offers?limit={limit}&offset={offset + limit}>; rel="next"'
    )

    cur.close()
    conn.close()

    # Convert DB dicts → Offer Pydantic objects
    return [Offer(**row) for row in rows]


# ---------------------------------------------------------
# POST /offers  (201 created + Location + hypermedia link)
# ---------------------------------------------------------
@router.post("/offers", response_model=Offer, status_code=201)
async def offers_post(offer: Offer, response: Response):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO offers (match_id, recipient_id, status)
        VALUES (%s, %s, %s)
        """,
        (offer.match_id, offer.recipient_id, offer.status),
    )

    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()

    offer.id = str(new_id)
    response.headers["Location"] = f"/offers/{new_id}"

    # Add hypermedia link
    return Offer(
        **offer.dict(),
        links={"self": f"/offers/{new_id}"}
    )
