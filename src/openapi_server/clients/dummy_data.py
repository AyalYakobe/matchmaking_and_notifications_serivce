#!/usr/bin/env python3

"""
Bulk Data Seeder for MS1 + MS2 via Composite API
- 4 hospitals
- 1000 recipients
- 1000 needs
- 1000 donors
- 1000 organs
- 1000 consents
"""

import requests
import random
from datetime import datetime, timedelta

BASE = "https://composite-service-730071231868.us-central1.run.app"

HOSPITAL_COUNT = 4
COUNT = 1000   # for everything else

# random helpers
def rand_date():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d")

def rand_ts():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).isoformat()

def rand_bt():
    return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

def rand_organ():
    return random.choice(["kidney", "heart", "liver", "lung"])

hospital_ids = []
recipient_ids = []
donor_ids = []

def post(url, payload):
    r = requests.post(url, json=payload)
    try:
        return r.json()
    except:
        print("Error:", r.text)
        return None

print(f"=== Creating Hospitals ({HOSPITAL_COUNT}) ===")
for i in range(HOSPITAL_COUNT):
    payload = {
        "name": f"Hospital {i}",
        "city": "CityX",
        "state": "StateY",
        "phone": "555-555-5555",
        "status": "active",
    }
    result = post(f"{BASE}/hospitals", payload)
    if result and "id" in result:
        hospital_ids.append(result["id"])

print(f"=== Creating Recipients ({COUNT}) ===")
for i in range(COUNT):
    hid = random.choice(hospital_ids)
    payload = {
        "full_name": f"Recipient {i}",
        "dob": rand_date(),
        "blood_type": rand_bt(),
        "status": "active",
        "primary_hospital_id": hid,
    }
    result = post(f"{BASE}/recipients", payload)
    if result and "id" in result:
        recipient_ids.append(result["id"])

print(f"=== Creating Needs ({COUNT}) ===")
for i in range(COUNT):
    rid = random.choice(recipient_ids)
    payload = {
        "recipient_id": rid,
        "organ_type": rand_organ(),
        "urgency": random.randint(1,5),
        "blood_type": rand_bt(),
        "status": "waiting",
    }
    post(f"{BASE}/needs", payload)

print(f"=== Creating Donors ({COUNT}) ===")
for i in range(COUNT):
    payload = {
        "full_name": f"Donor {i}",
        "dob": rand_date(),
        "blood_type": rand_bt(),
        "status": "active",
    }
    result = post(f"{BASE}/donors", payload)
    if result and "id" in result:
        donor_ids.append(result["id"])

print(f"=== Creating Organs ({COUNT}) ===")
for i in range(COUNT):
    did = random.choice(donor_ids)
    payload = {
        "organ_type": rand_organ(),
        "condition": "good",
        "retrieved_at": rand_ts(),
        "donor_id": did,
    }
    post(f"{BASE}/organs", payload)

print(f"=== Creating Consents ({COUNT}) ===")
for i in range(COUNT):
    did = random.choice(donor_ids)
    payload = {
        "donor_id": did,
        "scope": [rand_organ()],
        "status": "signed",
    }
    post(f"{BASE}/consents", payload)

print("=== DONE ===")
