import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from openapi_server.db.connection import get_connection
from openapi_server.models.offer import Offer, OfferCreate, OfferUpdate


# ---------------------------------------------------------
# Convert a raw DB row into Offer model-compatible dict
# ---------------------------------------------------------
def _convert_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(row.get("id")) if row.get("id") is not None else None,
        "matchId": str(row.get("matchId")),
        "recipientId": (
            str(row.get("recipientId"))
            if row.get("recipientId") is not None
            else None
        ),
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
        ),
    }


# ---------------------------------------------------------
# GET /offers
# ---------------------------------------------------------
async def get_offers(limit: int, offset: int) -> Tuple[List[Offer], str]:
    """
    Fetch offers from DB + generate ETag.
    Returns: (list of Offer, etag)
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

    # Create ETag based on deterministic JSON encoding
    body = json.dumps([o.model_dump(by_alias=True) for o in offers], default=str)
    etag = hashlib.sha1(body.encode()).hexdigest()

    return offers, etag


# ---------------------------------------------------------
# GET /offers/{id}
# ---------------------------------------------------------
async def get_offer(offer_id: int) -> Optional[Offer]:
    """
    Retrieve a single offer.
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
        WHERE id = %s
        """,
        (offer_id,),
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    return Offer.model_validate(_convert_row(row))


# ---------------------------------------------------------
# POST /offers
# ---------------------------------------------------------
async def create_offer(payload: OfferCreate) -> Offer:
    """
    Insert a new offer and return the full Offer record.
    """

    data = payload.model_dump(by_alias=True)
    now = datetime.utcnow()

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        INSERT INTO offers (match_id, recipient_id, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            data["matchId"],
            data["recipientId"],
            data.get("status") or "pending",
            now,
            now,
        ),
    )

    conn.commit()
    new_id = cur.lastrowid

    # Fetch inserted record
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
        (new_id,),
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    return Offer.model_validate(_convert_row(row))


# ---------------------------------------------------------
# PUT/PATCH /offers/{id}
# ---------------------------------------------------------
async def update_offer(offer_id: int, payload: OfferUpdate) -> Optional[Offer]:
    """
    Update offer fields.
    """
    updates = payload.model_dump(exclude_none=True, by_alias=True)

    if not updates:
        return await get_offer(offer_id)

    # Build SET clause dynamically
    set_clause = ", ".join([f"{key}=%s" for key in updates.keys()])
    values = list(updates.values())
    values.append(offer_id)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        f"""
        UPDATE offers
        SET {set_clause}, updated_at = %s
        WHERE id = %s
        """,
        (*updates.values(), datetime.utcnow(), offer_id),
    )

    conn.commit()
    cur.close()
    conn.close()

    return await get_offer(offer_id)


# ---------------------------------------------------------
# DELETE /offers/{id}
# ---------------------------------------------------------
async def delete_offer(offer_id: int) -> bool:
    """
    Delete an offer.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM offers WHERE id = %s", (offer_id,))
    deleted = cur.rowcount > 0

    conn.commit()
    cur.close()
    conn.close()

    return deleted
