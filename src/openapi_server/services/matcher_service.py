# src/openapi_server/services/matcher.py

from typing import List, Dict
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client
from openapi_server.db.connection import get_connection


class Matcher:
    """
    Performs donor-organ ↔ recipient-need matching via the composite API,
    applies compatibility rules, deletes consumed resources, and
    saves match results to the SQL database.
    """

    def __init__(self, ms1_base_url: str, ms2_base_url: str):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    # -----------------------------------------
    # BLOOD TYPE COMPATIBILITY
    # -----------------------------------------
    def is_compatible(self, donor_bt: str, recipient_bt: str) -> bool:
        """Compatibility logic for organ transplantation."""

        d = donor_bt.replace("+", "").replace("-", "")
        r = recipient_bt.replace("+", "").replace("-", "")

        rules = {
            "O": ["O", "A", "B", "AB"],
            "A": ["A", "AB"],
            "B": ["B", "AB"],
            "AB": ["AB"]
        }

        return r in rules[d]

    # -----------------------------------------
    # SAVE MATCH TO DATABASE
    # -----------------------------------------
    def save_to_db(self, match: Dict):
        """Insert match record into SQL database."""
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

    # -----------------------------------------
    # MATCHING LOGIC
    # -----------------------------------------
    def match_and_consume(self) -> List[Dict]:
        """
        - Fetch organs and needs
        - Match based on organ type + blood type
        - Insert match into DB
        - Delete used organ + need from MS1/MS2
        - Return match list
        """

        organs = self.ms1.list_organs()
        needs = self.ms2.list_needs()

        results = []

        for organ in organs:
            organ_type = organ["type"]
            donor_bt = organ["blood_type"]

            # Match same organ type AND compatible blood type
            need = next((
                n for n in needs
                if n["organ_type"] == organ_type
                and self.is_compatible(donor_bt, n["blood_type"])
            ), None)

            if not need:
                continue

            # Build match record
            match_entry = {
                "donor_id": organ["donor_id"],
                "organ_id": organ["id"],
                "recipient_id": need["recipient_id"],
                "donor_blood_type": donor_bt,
                "recipient_blood_type": need["blood_type"],
                "organ_type": organ_type,
                "score": 1.0,
                "status": "matched",  # NEW STATUS
            }

            results.append(match_entry)

            # Save match to DB
            self.save_to_db(match_entry)

            # Delete organ + need from microservices
            self.ms1.delete_organ(organ["id"])
            self.ms2.delete_need(need["id"])

            # Remove from in-memory list
            needs = [n for n in needs if n["id"] != need["id"]]

        return results

    def paginate(self, items: List[Dict], limit: int, offset: int) -> List[Dict]:
        return items[offset: offset + limit]
