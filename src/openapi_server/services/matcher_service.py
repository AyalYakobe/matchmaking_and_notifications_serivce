# src/openapi_server/services/matcher.py

from typing import List, Dict
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client


class Matcher:
    """
    Performs donor-organ ↔ recipient-need matching via the composite API.
    """

    def __init__(self, ms1_base_url: str, ms2_base_url: str):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    def match_and_consume(self) -> List[Dict]:
        """
        Returns DB-ready match dictionaries.
        Deletes matched organs/needs from MS1/MS2.
        """

        organs = self.ms1.list_organs()
        needs = self.ms2.list_needs()

        results = []

        for organ in organs:
            organ_type = organ["type"]

            # Match need with same organ type
            need = next((n for n in needs if n["organ_type"] == organ_type), None)
            if not need:
                continue

            # Build the match object
            match_entry = {
                "donor_id": organ["donor_id"],
                "organ_id": organ["id"],
                "recipient_id": need["recipient_id"],
                "donor_blood_type": organ["blood_type"],
                "recipient_blood_type": need["blood_type"],
                "organ_type": organ_type,
                "score": 1.0,
                "status": "matched",
            }

            results.append(match_entry)

            # Consume organ and need
            self.ms1.delete_organ(organ["id"])
            self.ms2.delete_need(need["id"])

            # Remove consumed need
            needs = [n for n in needs if n["id"] != need["id"]]

        return results

    def paginate(self, items: List[Dict], limit: int, offset: int) -> List[Dict]:
        """Utility to paginate lists."""
        return items[offset: offset + limit]
