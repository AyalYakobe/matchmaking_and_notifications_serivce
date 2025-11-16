from typing import List, Optional
from fastapi import Response, HTTPException

from openapi_server.models.match import Match
from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.impl.db import get_connection


class MatchesApiImpl(BaseDefaultApi):

    # -------------------------------------------------------------
    # GET /matches  (with filters + pagination)
    # -------------------------------------------------------------
    async def matches_get(
        self,
        limit: int,
        offset: int,
        donor_id: Optional[str],
        recipient_id: Optional[str],
        response: Response
    ) -> List[Match]:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT 
                id,
                donor_id AS donorId,
                organ_id AS organId,
                recipient_id AS recipientId,
                donor_blood_type AS donorBloodType,
                recipient_blood_type AS recipientBloodType,
                organ_type AS organType,
                score,
                status
            FROM matches
            WHERE 1=1
        """

        params = []

        if donor_id:
            query += " AND donor_id = %s"
            params.append(donor_id)

        if recipient_id:
            query += " AND recipient_id = %s"
            params.append(recipient_id)

        query += " ORDER BY id ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [Match(**row) for row in rows]

    # -------------------------------------------------------------
    # POST /matches
    # -------------------------------------------------------------
    async def matches_post(self, match: Match, response: Response) -> Match:

        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO matches 
                (donor_id, organ_id, recipient_id,
                 donor_blood_type, recipient_blood_type, organ_type,
                 score, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(
            query,
            (
                match.donor_id,
                match.organ_id,
                match.recipient_id,
                match.donor_blood_type,
                match.recipient_blood_type,
                match.organ_type,
                match.score,
                match.status,
            ),
        )
        conn.commit()

        match_id = cur.lastrowid
        match.id = str(match_id)

        cur.close()
        conn.close()

        response.status_code = 201
        response.headers["Location"] = f"/matches/{match.id}"
        return match

    # -------------------------------------------------------------
    # GET /matches/{id}
    # -------------------------------------------------------------
    async def matches_id_get(self, id: str) -> Match:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT 
                id,
                donor_id AS donorId,
                organ_id AS organId,
                recipient_id AS recipientId,
                donor_blood_type AS donorBloodType,
                recipient_blood_type AS recipientBloodType,
                organ_type AS organType,
                score,
                status
            FROM matches
            WHERE id = %s
            """,
            (id,),
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Match not found")

        return Match(**row)

    # -------------------------------------------------------------
    # DELETE /matches/{id}
    # -------------------------------------------------------------
    async def matches_id_delete(self, id: str) -> None:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM matches WHERE id=%s", (id,))
        conn.commit()

        deleted = cur.rowcount

        cur.close()
        conn.close()

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Match not found")

        return None
