# matcher.py
from ms1_client import MS1Client
from ms2_client import MS2Client

class Matcher:
    def __init__(self, ms1_base_url, ms2_base_url):
        self.ms1 = MS1Client(ms1_base_url)
        self.ms2 = MS2Client(ms2_base_url)

    def match_and_consume(self):
        organs = self.ms1.list_organs()
        needs = self.ms2.list_needs()

        matches = []

        for organ in organs:
            organ_type = organ["type"]

            # find need with same organ_type
            need = next((n for n in needs if n["organ_type"] == organ_type), None)
            if not need:
                continue

            # build match entry
            matches.append({
                "organ_id": organ["id"],
                "need_id": need["id"],
                "recipient_id": need["recipient_id"],
                "organ_type": organ_type
            })

            # DELETE matched resources
            self.ms1.delete_organ(organ["id"])
            self.ms2.delete_need(need["id"])

            # remove consumed need from list
            needs = [n for n in needs if n["id"] != need["id"]]

        return matches
