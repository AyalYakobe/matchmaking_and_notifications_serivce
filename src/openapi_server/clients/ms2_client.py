# ms2_client.py
import requests

class MS2Client:
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
    # Recipients
    # -----------------------------

    def list_recipients(self):
        return self._get("/recipients")

    def get_recipient(self, recipient_id):
        return self._get(f"/recipients/{recipient_id}")

    def create_recipient(self, payload):
        return self._post("/recipients", payload)

    def update_recipient(self, recipient_id, payload):
        return self._put(f"/recipients/{recipient_id}", payload)

    def delete_recipient(self, recipient_id):
        return self._delete(f"/recipients/{recipient_id}")

    # -----------------------------
    # Needs (organ needs)
    # -----------------------------

    def list_needs(self):
        return self._get("/needs")

    def get_need(self, need_id):
        return self._get(f"/needs/{need_id}")

    def create_need(self, payload):
        return self._post("/needs", payload)

    def update_need(self, need_id, payload):
        return self._put(f"/needs/{need_id}", payload)

    def delete_need(self, need_id):
        return self._delete(f"/needs/{need_id}")

    def list_needs_for_recipient(self, recipient_id):
        return self._get(f"/recipients/{recipient_id}/needs")

    def create_need_for_recipient(self, recipient_id, payload):
        return self._post(f"/recipients/{recipient_id}/needs", payload)

    # -----------------------------
    # Hospitals
    # -----------------------------

    def list_hospitals(self):
        return self._get("/hospitals")

    def get_hospital(self, hospital_id):
        return self._get(f"/hospitals/{hospital_id}")

    def create_hospital(self, payload):
        return self._post("/hospitals", payload)

    def update_hospital(self, hospital_id, payload):
        return self._put(f"/hospitals/{hospital_id}", payload)

    def delete_hospital(self, hospital_id):
        return self._delete(f"/hospitals/{hospital_id}")
