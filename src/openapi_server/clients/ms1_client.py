import requests


class MS1Client:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    # ---------------------------------------------------------
    # Internal request helpers
    # ---------------------------------------------------------
    def _get(self, path):
        r = requests.get(f"{self.base}{path}")
        r.raise_for_status()
        return r.json()

    def _post(self, path, payload):
        r = requests.post(f"{self.base}{path}", json=payload)
        r.raise_for_status()
        return r.json()

    def _put(self, path, payload):
        r = requests.put(f"{self.base}{path}", json=payload)
        r.raise_for_status()
        return r.json()

    def _delete(self, path):
        r = requests.delete(f"{self.base}{path}")
        r.raise_for_status()
        return True

    # ---------------------------------------------------------
    # HAL → FLAT transformation
    # MS1 returns:
    # {
    #   "items": [ { "data": {...}, "_links": {...} } ],
    #   "count": 1,
    #   "total": 1
    # }
    #
    # We extract ONLY the "data" part.
    # ---------------------------------------------------------
    def _flat(self, wrapper):
        if not isinstance(wrapper, dict):
            return []
        if "items" not in wrapper:
            return []
        return [item["data"] for item in wrapper["items"]]

    # ---------------------------------------------------------
    # Donors
    # ---------------------------------------------------------
    def list_donors(self):
        """Return donors as a flat list of dicts."""
        return self._flat(self._get("/donors"))

    def get_donor(self, donor_id):
        """Return a single donor's FLAT data."""
        return self._get(f"/donors/{donor_id}")

    # ---------------------------------------------------------
    # Organs
    # ---------------------------------------------------------
    def list_organs(self):
        """
        Return organs as FLAT objects AND attach donor blood type
        so the matcher has a complete organ record.
        """
        raw = self._get("/organs")
        organs = self._flat(raw)

        for organ in organs:
            donor = self.get_donor(organ["donor_id"])
            organ["blood_type"] = donor["blood_type"]

        return organs

    def get_organ(self, organ_id):
        organ = self._get(f"/organs/{organ_id}")
        # flatten organ (it returns single object, not HAL)
        if "data" in organ:
            organ = organ["data"]
        # attach donor blood type
        donor = self.get_donor(organ["donor_id"])
        organ["blood_type"] = donor["blood_type"]
        return organ

    def create_organ(self, donor_id, payload):
        return self._post(f"/donors/{donor_id}/organs", payload)

    def update_organ(self, organ_id, payload):
        return self._put(f"/organs/{organ_id}", payload)

    def delete_organ(self, organ_id):
        return self._delete(f"/organs/{organ_id}")

    def list_organs_for_donor(self, donor_id):
        raw = self._get(f"/donors/{donor_id}/organs")
        organs = self._flat(raw)
        for organ in organs:
            donor = self.get_donor(organ["donor_id"])
            organ["blood_type"] = donor["blood_type"]
        return organs

    # ---------------------------------------------------------
    # Consents
    # ---------------------------------------------------------
    def list_consents(self):
        return self._flat(self._get("/consents"))

    def get_consent(self, consent_id):
        c = self._get(f"/consents/{consent_id}")
        return c["data"] if "data" in c else c

    def create_consent(self, donor_id, payload):
        return self._post(f"/donors/{donor_id}/consents", payload)

    def update_consent(self, consent_id, payload):
        return self._put(f"/consents/{consent_id}", payload)

    def delete_consent(self, consent_id):
        return self._delete(f"/consents/{consent_id}")
