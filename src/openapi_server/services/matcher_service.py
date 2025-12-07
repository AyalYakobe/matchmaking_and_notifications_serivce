from typing import List, Dict, Optional
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client
from openapi_server.db.connection import get_connection
from openapi_server.clients.pubsub_client import publish_event
from openapi_server.models.match_model import Match, MatchCreate, MatchUpdate


class Matcher:
    """
    Performs donor-organ ↔ recipient matching and persistence.
    """

    def __init__(self, ms1_base_url: str, ms2_base_url: str):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    # ---------------------------------------------------------
    # BLOOD COMPATIBILITY
    # ---------------------------------------------------------
    def is_compatible(self, donor_bt: str, recipient_bt: str) -> bool:
        d = donor_bt.replace("+", "").replace("-", "")
        r = recipient_bt.replace("+", "").replace("-", "")
        rules = {
            "O": ["O", "A", "B", "AB"],
            "A": ["A", "AB"],
            "B": ["B", "AB"],
            "AB": ["AB"],
        }
        return d in rules and r in rules[d]

    # ---------------------------------------------------------
    # SQL INSERT
    # ---------------------------------------------------------
    def save_to_db(self, match: Dict) -> int:
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO matches
            (donor_id, organ_id, recipient_id,
             donor_blood_type, recipient_blood_type,
             organ_type, score, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(sql, (
            match["donor_id"],
            match["organ_id"],
            match["recipient_id"],
            match["donor_blood_type"],
            match["recipient_blood_type"],
            match["organ_type"],
            match["score"],
            match["status"]
        ))

        match_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return match_id

    # ---------------------------------------------------------
    # CREATE OFFER
    # ---------------------------------------------------------
    def create_offer(self, match_id: int, recipient_id: str):
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO offers (match_id, recipient_id, status)
            VALUES (%s, %s, %s)
        """

        cur.execute(sql, (match_id, recipient_id, "pending"))
        conn.commit()
        cur.close()
        conn.close()

    # ---------------------------------------------------------
    # MATCHING LOGIC
    # ---------------------------------------------------------
    def match_and_consume(self) -> List[Dict]:
        organs_raw = self.ms1.list_organs()
        needs = self.ms2.list_needs()
        results: List[Dict] = []

        for organ in organs_raw:
            o = organ.get("data", organ)
            organ_type = o["organ_type"]
            donor_bt = o.get("blood_type", "O+")
            donor_id = o["donor_id"]
            organ_id = o["id"]

            need = next((
                n for n in needs
                if n["organ_type"] == organ_type
                and self.is_compatible(donor_bt, n["blood_type"])
            ), None)

            if not need:
                continue

            match_entry = {
                "donor_id": donor_id,
                "organ_id": organ_id,
                "recipient_id": need["recipient_id"],
                "donor_blood_type": donor_bt,
                "recipient_blood_type": need["blood_type"],
                "organ_type": organ_type,
                "score": 1.0,
                "status": "matched",
            }

            match_id = self.save_to_db(match_entry)
            self.create_offer(match_id, need["recipient_id"])

            publish_event({
                "match_id": match_id,
                "donor_id": donor_id,
                "organ_id": organ_id,
                "recipient_id": need["recipient_id"],
                "organ_type": organ_type,
                "message": "New donor-recipient match created"
            })

            match_entry["match_id"] = match_id
            results.append(match_entry)

            self.ms1.delete_organ(organ_id)
            self.ms2.delete_need(need["id"])
            needs = [n for n in needs if n["id"] != need["id"]]

        return results


    # ==========================================================
    # =============== CRUD FUNCTIONS FOR API ===================
    # ==========================================================

def list_matches():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM matches ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_match(match_id: int) -> Optional[Dict]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_match(payload: MatchCreate) -> Dict:
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO matches
        (donor_id, organ_id, recipient_id,
         donor_blood_type, recipient_blood_type,
         organ_type, score, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    data = payload.model_dump(by_alias=True)

    cur.execute(sql, (
        data["donorId"], data["organId"], data.get("recipientId"),
        data.get("donorBloodType"), data.get("recipientBloodType"),
        data.get("organType"), data.get("score"), data.get("status")
    ))

    match_id = cur.lastrowid
    conn.commit()

    cur.close()
    conn.close()
    return get_match(match_id)


def update_match(match_id: int, payload: MatchUpdate) -> Optional[Dict]:
    updates = payload.model_dump(exclude_none=True, by_alias=True)
    if not updates:
        return get_match(match_id)

    set_clause = ", ".join([f"{key}=%s" for key in updates.keys()])
    values = list(updates.values())

    conn = get_connection()
    cur = conn.cursor()
    sql = f"UPDATE matches SET {set_clause} WHERE id = %s"
    cur.execute(sql, (*values, match_id))
    conn.commit()
    cur.close()
    conn.close()

    return get_match(match_id)


def delete_match(match_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM matches WHERE id = %s", (match_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return deleted


def get_full_match(match_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
    match = cur.fetchone()

    if not match:
        cur.close()
        conn.close()
        return None

    cur.execute("SELECT * FROM offers WHERE match_id = %s", (match_id,))
    offers = cur.fetchall()

    cur.close()
    conn.close()

    return {"match": match, "offers": offers}
