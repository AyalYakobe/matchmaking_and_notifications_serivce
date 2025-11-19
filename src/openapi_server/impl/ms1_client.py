# ms1_client.py
import requests

class MS1Client:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _get(self, path):
        r = requests.get(f"{self.base_url}{path}")
        r.raise_for_status()
        return r.json()

    def _post(self, path, payload):
        r = requests.post(f"{self.base_url}{path}", json=payload)
        r.raise_for_status()
        return r.json()

    def _put(self, path, payload):
        r = requests.put(f"{self.base_url}{path}", json=payload)
        r.raise_for_status()
        return r.json()

    def _delete(self, path):
        r = requests.delete(f"{self.base_url}{path}")
        r.raise_for_status()
        return True

    # -----------------------------
    # Donors
    # -----------------------------

    def list_donors(self):
        return self._get("/donors")

    def get_donor(self, donor_id):
        return self._get(f"/donors/{donor_id}")

    def create_donor(self, payload):
        return self._post("/donors", payload)

    def update_donor(self, donor_id, payload):
        return self._put(f"/donors/{donor_id}", payload)

    def delete_donor(self, donor_id):
        return self._delete(f"/donors/{donor_id}")

    # -----------------------------
    # Organs
    # -----------------------------

    def list_organs(self):
        return self._get("/organs")

    def get_organ(self, organ_id):
        return self._get(f"/organs/{organ_id}")

    def create_organ(self, donor_id, payload):
        return self._post(f"/donors/{donor_id}/organs", payload)

    def update_organ(self, organ_id, payload):
        return self._put(f"/organs/{organ_id}", payload)

    def delete_organ(self, organ_id):
        return self._delete(f"/organs/{organ_id}")

    def list_organs_for_donor(self, donor_id):
        return self._get(f"/donors/{donor_id}/organs")

    # -----------------------------
    # Consents
    # -----------------------------

    def list_consents(self):
        return self._get("/consents")

    def get_consent(self, consent_id):
        return self._get(f"/consents/{consent_id}")

    def create_consent(self, donor_id, payload):
        return self._post(f"/donors/{donor_id}/consents", payload)

    def update_consent(self, consent_id, payload):
        return self._put(f"/consents/{consent_id}", payload)

    def delete_consent(self, consent_id):
        return self._delete(f"/consents/{consent_id}")
