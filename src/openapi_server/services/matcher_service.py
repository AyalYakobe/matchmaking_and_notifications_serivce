# src/openapi_server/services/matcher.py

from typing import List, Dict
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client
from openapi_server.db.connection import get_connection
from openapi_server.clients.pubsub_client import publish_event



class Matcher:
    """
    Performs donor-organ ↔ recipient-need matching via composite API,
    with organ-type + blood-type compatibility, deletion of consumed
    records in MS1/MS2, saving matches to SQL, and auto-creating offers.
    """

    def __init__(self, ms1_base_url: str, ms2_base_url: str):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    # ---------------------------------------------------------
    # BLOOD TYPE COMPATIBILITY RULES
    # ---------------------------------------------------------
    def is_compatible(self, donor_bt: str, recipient_bt: str) -> bool:
        """Determine blood-type compatibility."""

        d = donor_bt.replace("+", "").replace("-", "")
        r = recipient_bt.replace("+", "").replace("-", "")

        rules = {
            "O": ["O", "A", "B", "AB"],
            "A": ["A", "AB"],
            "B": ["B", "AB"],
            "AB": ["AB"],
        }

        if d not in rules:
            return False

        return r in rules[d]

    # ---------------------------------------------------------
    # SAVE MATCH → SQL AND RETURN NEW match_id
    # ---------------------------------------------------------
    def save_to_db(self, match: Dict) -> int:
        """Write a match record into MySQL matches table and return inserted ID."""
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
    # CREATE OFFER AUTOMATICALLY
    # ---------------------------------------------------------
    def create_offer(self, match_id: int, recipient_id: str):
        """Insert a new offer for a matched recipient."""
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
        """
        Steps:
        1. Fetch organs + needs from MS1/MS2
        2. Unwrap organ data (Composite returns flat objects)
        3. Match on organ_type + blood-type compatibility
        4. Save match to SQL (get match_id)
        5. Auto-create offer using match_id
        6. Publish Pub/Sub event (TRIGGERS CLOUD FUNCTION)
        7. Delete matched organ + need
        8. Return list of matches
        """

        organs_raw = self.ms1.list_organs()
        needs = self.ms2.list_needs()

        results: List[Dict] = []

        for organ in organs_raw:

            # Composite returns flat JSON; older MS1 returned {"data": ...}
            o = organ.get("data", organ)

            organ_type = o["organ_type"]
            donor_bt = o.get("blood_type", "O+")
            donor_id = o["donor_id"]
            organ_id = o["id"]

            # ---- find compatible need ----
            need = next((
                n for n in needs
                if n["organ_type"] == organ_type
                and self.is_compatible(donor_bt, n["blood_type"])
            ), None)

            if not need:
                continue

            # ---- build match record ----
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

            # 1️ Save match to database and get match_id
            match_id = self.save_to_db(match_entry)

            # 2️ Auto-create offer
            self.create_offer(match_id, need["recipient_id"])

            # 3️ Publish Pub/Sub event to trigger Cloud Function
            publish_event({
                "match_id": match_id,
                "donor_id": donor_id,
                "organ_id": organ_id,
                "recipient_id": need["recipient_id"],
                "organ_type": organ_type,
                "message": "New donor-recipient match created"
            })

            # 4️ Add to API response
            match_entry["match_id"] = match_id
            results.append(match_entry)

            # 5️ Delete consumed organ + need
            self.ms1.delete_organ(organ_id)
            self.ms2.delete_need(need["id"])

            # 6️ Remove matched need from list to avoid duplicates
            needs = [n for n in needs if n["id"] != need["id"]]

        return results

    # ---------------------------------------------------------
    # OPTIONAL PAGINATION
    # ---------------------------------------------------------
    def paginate(self, items: List[Dict], limit: int, offset: int) -> List[Dict]:
        return items[offset: offset + limit]
