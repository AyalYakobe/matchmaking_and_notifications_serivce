import hashlib
import json
from fastapi import Response, HTTPException

from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.offer import Offer
from openapi_server.impl.db import get_connection


class OffersService(BaseDefaultApi):

    # -------------------------------------------------------------
    # GET /offers
    # -------------------------------------------------------------
    async def offers_get(self, limit, offset, response: Response):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
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
        """

        cur.execute(query, (limit, offset))
        rows = cur.fetchall()

        # ETag generation
        body = json.dumps(rows, default=str)
        etag = hashlib.sha1(body.encode()).hexdigest()
        response.headers["ETag"] = etag

        # Pagination header
        response.headers["Link"] = (
            f'</offers?limit={limit}&offset={offset+limit}>; rel="next"'
        )

        cur.close()
        conn.close()

        # Convert DB rows → Pydantic Offer objects
        return [Offer(**row) for row in rows]

    # -------------------------------------------------------------
    # POST /offers
    # -------------------------------------------------------------
    async def offers_post(self, offer: Offer, response: Response):
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO offers (match_id, recipient_id, status)
            VALUES (%s, %s, %s)
        """

        cur.execute(query, (offer.match_id, offer.recipient_id, offer.status))
        conn.commit()

        # New DB ID
        new_id = cur.lastrowid
        offer.id = str(new_id)

        cur.close()
        conn.close()

        # Set response headers
        response.status_code = 201
        response.headers["Location"] = f"/offers/{new_id}"

        # Add links like your original output
        return Offer(**offer.dict(), links={"self": f"/offers/{new_id}"})
