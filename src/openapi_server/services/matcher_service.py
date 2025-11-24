# src/openapi_server/services/matcher.py

from typing import List, Dict
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client
from openapi_server.db.connection import get_connection


class Matcher:
    """
    Performs donor-organ ↔ recipient-need matching via composite API,
    with organ-type + blood-type compatibility, deletion of consumed
    records in MS1/MS2, and saving match results to SQL database.
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
    # SAVE MATCH INTO SQL DB
    # ---------------------------------------------------------
    def save_to_db(self, match: Dict):
        """Write a match record into MySQL matches table."""
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
        2. unwrap organ data (Composite returns flat objects)
        3. match on organ_type + blood-type compatibility
        4. save match to SQL DB
        5. delete organ + need from MS1/MS2
        6. return list of match results
        """

        organs_raw = self.ms1.list_organs()
        needs = self.ms2.list_needs()

        results: List[Dict] = []

        for organ in organs_raw:

            # ---- FIXED: unwrap flat composite structure or {"data": {...}} ----
            o = organ.get("data", organ)

            # Required fields
            organ_type = o["organ_type"]
            donor_bt = o.get("blood_type", "O+")     # default if missing
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

            # ---- build match object ----
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

            # Save → MySQL
            self.save_to_db(match_entry)

            # Append to API response
            results.append(match_entry)

            # Delete consumed organ + need from MS1/MS2
            self.ms1.delete_organ(organ_id)
            self.ms2.delete_need(need["id"])

            # Remove from in-memory list to avoid matching again
            needs = [n for n in needs if n["id"] != need["id"]]

        return results

    # ---------------------------------------------------------
    # OPTIONAL: Pagination Helper
    # ---------------------------------------------------------
    def paginate(self, items: List[Dict], limit: int, offset: int) -> List[Dict]:
        return items[offset: offset + limit]
