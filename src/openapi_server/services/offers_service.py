# src/openapi_server/services/offers_service.py

import hashlib
import json
from fastapi import Response, HTTPException

from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.offer import Offer
from openapi_server.db.connection import get_connection


class OffersService(BaseDefaultApi):

    async def offers_get(self, limit, offset, response: Response):
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

        # ETag
        body = json.dumps(rows, default=str)
        etag = hashlib.sha1(body.encode()).hexdigest()
        response.headers["ETag"] = etag

        # Pagination header
        response.headers["Link"] = (
            f'</offers?limit={limit}&offset={offset + limit}>; rel="next"'
        )

        cur.close()
        conn.close()

        return [Offer(**row) for row in rows]

    async def offers_post(self, offer: Offer, response: Response):
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
        offer.id = str(new_id)

        cur.close()
        conn.close()

        response.status_code = 201
        response.headers["Location"] = f"/offers/{new_id}"

        return Offer(
            **offer.dict(),
            links={"self": f"/offers/{new_id}"}
        )
