# services/offers_service.py

import json
import hashlib
from typing import List, Dict, Any

from openapi_server.db.connection import get_connection
from openapi_server.models.offer import Offer


def get_offers(limit: int, offset: int) -> tuple[List[Offer], str]:
    """
    Fetch offers from DB + generate ETag.
    Returns: (list of offers, etag)
    """
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
    cur.close()
    conn.close()

    # Create Pydantic Offer models
    offers = [Offer(**row) for row in rows]

    # Build ETag from the serialized response body
    body = json.dumps([o.dict() for o in offers], default=str)
    etag = hashlib.sha1(body.encode()).hexdigest()

    return offers, etag


def create_offer(offer: Offer) -> Offer:
    """Insert a new offer and return model containing its new ID."""
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
    return offer
