# coding: utf-8
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import StrictStr

from openapi_server.db.connection import get_connection
from openapi_server.models.match import Match
from openapi_server.models.offer import Offer

router = APIRouter()

# -----------------------------------------------------------
# HEALTH
# -----------------------------------------------------------
@router.get("/health", tags=["default"])
async def health_get():
    return {"status": "ok", "service": "MS3 Matchmaking & Notification"}


# -----------------------------------------------------------
# MATCHES (DB-BACKED)
# -----------------------------------------------------------
@router.get("/matches", tags=["matches"])
async def matches_get(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    donor_id: Optional[str] = Query(None),
    recipient_id: Optional[str] = Query(None),
):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM matches WHERE 1=1"
    params = []

    if donor_id:
        sql += " AND donor_id = %s"
        params.append(donor_id)

    if recipient_id:
        sql += " AND recipient_id = %s"
        params.append(recipient_id)

    sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cur.execute(sql, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


@router.get("/matches/{id}", tags=["matches"])
async def matches_id_get(id: int, response: Response):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM matches WHERE id = %s", (id,))
    match = cur.fetchone()

    cur.close()
    conn.close()

    if not match:
        raise HTTPException(status_code=404, detail=f"Match {id} not found")

    response.headers["ETag"] = f'W/"match-{id}-{match["status"]}"'
    return match


@router.get("/matches/{id}/full", tags=["matches"])
async def get_full_match(id: int):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # main match
    cur.execute("SELECT * FROM matches WHERE id = %s", (id,))
    match = cur.fetchone()

    if not match:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match {id} not found")

    # all offers linked to this match
    cur.execute("SELECT * FROM offers WHERE match_id = %s", (id,))
    offers = cur.fetchall()

    cur.close()
    conn.close()

    return {"match": match, "offers": offers}


# -----------------------------------------------------------
# OFFERS
# -----------------------------------------------------------
@router.get("/offers", tags=["offers"])
async def offers_list(matchId: Optional[int] = Query(None)):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if matchId:
        cur.execute("SELECT * FROM offers WHERE match_id = %s", (matchId,))
    else:
        cur.execute("SELECT * FROM offers ORDER BY created_at DESC")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


@router.get("/offers/{offer_id}", tags=["offers"])
async def offers_id_get(offer_id: int):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM offers WHERE id = %s", (offer_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

    return row
