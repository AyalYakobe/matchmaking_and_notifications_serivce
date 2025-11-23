# matcher.py

from typing import List, Dict
from openapi_server.impl.ms1_client import MS1Client
from openapi_server.impl.ms2_client import MS2Client


class Matcher:
    """
    Orchestrates donor-organ ↔ recipient-need matching.

    Responsibilities:
    -----------------
    1. Fetch organs from MS1
    2. Fetch needs from MS2
    3. Match organ_type to organ_type
    4. Build DB-ready match dicts
    5. DELETE the organ + need after matching (consumption)
    6. Return a list of match dictionaries
    """

    def __init__(self, ms1_base_url: str, ms2_base_url: str):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    # ------------------------------------------------------------------
    # Core matching logic
    # ------------------------------------------------------------------
    def match_and_consume(self) -> List[Dict]:
        """
        Return a list of DB-ready match dictionaries:

        {
            "donor_id": ...,
            "organ_id": ...,
            "recipient_id": ...,
            "donor_blood_type": ...,
            "recipient_blood_type": ...,
            "organ_type": ...,
            "score": float,
            "status": "matched"
        }
        """

        organs = self.ms1.list_organs()
        needs = self.ms2.list_needs()
        results = []

        for organ in organs:
            organ_type = organ["type"]

            # Match need with same organ_type
            need = next((n for n in needs if n["organ_type"] == organ_type), None)
            if not need:
                continue

            # ------------------------------------------------------------------
            #  Build DB-ready match object
            #  (These keys match your SQL schema)
            # ------------------------------------------------------------------
            match_entry = {
                "donor_id": organ["donor_id"],
                "organ_id": organ["id"],
                "recipient_id": need["recipient_id"],

                "donor_blood_type": organ["blood_type"],
                "recipient_blood_type": need["blood_type"],

                "organ_type": organ_type,

                # TODO: You can replace score with real compatibility logic.
                "score": 1.0,
                "status": "matched",
            }
            results.append(match_entry)

            # ------------------------------------------------------------------
            #  Consume matched resources
            # ------------------------------------------------------------------
            self.ms1.delete_organ(organ["id"])
            self.ms2.delete_need(need["id"])

            # Remove need from local list (avoid double-consumption)
            needs = [n for n in needs if n["id"] != need["id"]]

        return results

    def paginate(self, items: List[Dict], limit: int, offset: int) -> List[Dict]:
        """
        Slice list according to limit + offset.
        Useful if you want to paginate results BEFORE DB insertion.
        """
        return items[offset: offset + limit]
