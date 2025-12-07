# services/offers_service.py

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple

from openapi_server.db.connection import get_connection
from openapi_server.models.offer import Offer


def _convert_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DB row into strings required by the Offer model."""
    return {
        "id": str(row.get("id")) if row.get("id") is not None else None,
        "matchId": str(row.get("matchId")),
        "recipientId": str(row.get("recipientId")) if row.get("recipientId") else None,
        "status": row.get("status"),
        "createdAt": (
            row["createdAt"].isoformat()
            if isinstance(row.get("createdAt"), datetime)
            else row.get("createdAt")
        ),
        "updatedAt": (
            row["updatedAt"].isoformat()
            if isinstance(row.get("updatedAt"), datetime)
            else row.get("updatedAt")
        )
    }


async def get_offers(limit: int, offset: int) -> Tuple[List[Offer], str]:
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

    converted = [_convert_row(r) for r in rows]
    offers = [Offer.model_validate(c) for c in converted]

    # Build ETag
    body = json.dumps([o.model_dump(by_alias=True) for o in offers], default=str)
    etag = hashlib.sha1(body.encode()).hexdigest()

    return offers, etag


async def create_offer(offer: Offer) -> Offer:
    """Insert a new offer and return full Offer model."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    now = datetime.utcnow()

    cur.execute(
        """
        INSERT INTO offers (match_id, recipient_id, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (offer.match_id, offer.recipient_id, offer.status, now, now),
    )

    conn.commit()

    new_id = cur.lastrowid

    # Retrieve full record including timestamps
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
        WHERE id = %s
        """,
        (new_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    return Offer.model_validate(_convert_row(row))
