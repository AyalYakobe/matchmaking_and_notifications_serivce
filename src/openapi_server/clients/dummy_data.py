#!/usr/bin/env python3
"""
Bulk Data Seeder for MS1 + MS2 via Composite API
- 4 hospitals
- 50 recipients
- 50 needs
- 50 donors
- 50 organs
- 50 consents

50% will be MATCHABLE
50% will be UNMATCHABLE
"""

import requests
import random
from datetime import datetime, timedelta

BASE = "https://composite-service-730071231868.us-central1.run.app"

HOSPITAL_COUNT = 4
COUNT = 50   # Everything else = 50

# random helpers
def rand_date():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d")

def rand_ts():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).isoformat()

def rand_bt():
    return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

def rand_organ():
    return random.choice(["kidney", "heart", "liver", "lung"])

# BLOOD TYPE COMPATIBILITY RULES
compatible_map = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}

def base_type(bt):
    return bt.replace("+", "").replace("-", "")

def get_compatible(bt):
    base = base_type(bt)
    return compatible_map[base]

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


# -------------------------
# HOSPITALS
# -------------------------
print(f"=== Creating Hospitals ({HOSPITAL_COUNT}) ===")
for i in range(HOSPITAL_COUNT):
    result = post(f"{BASE}/hospitals", {
        "name": f"Hospital {i}",
        "city": "CityX",
        "state": "StateY",
        "phone": "555-555-5555",
        "status": "active",
    })
    if result and "id" in result:
        hospital_ids.append(result["id"])


# -------------------------
# RECIPIENTS
# -------------------------
print(f"=== Creating Recipients ({COUNT}) ===")
recipient_btypes = []
for i in range(COUNT):
    b = rand_bt()
    recipient_btypes.append(b)

    result = post(f"{BASE}/recipients", {
        "full_name": f"Recipient {i}",
        "dob": rand_date(),
        "blood_type": b,
        "status": "active",
        "primary_hospital_id": random.choice(hospital_ids),
    })
    if result and "id" in result:
        recipient_ids.append(result["id"])


# -------------------------
# NEEDS (50% MATCHABLE)
# -------------------------
print(f"=== Creating Needs ({COUNT}) ===")
needs = []
for i in range(COUNT):
    rid = recipient_ids[i]
    base_bt = base_type(recipient_btypes[i])

    # 50% MATCHABLE NEEDS
    if i < COUNT // 2:
        organ_type = "kidney"       # consistent matchable organ
        blood_type = recipient_btypes[i]
    else:
        # UNMATCHABLE: random organ or incompatible blood type
        organ_type = random.choice(["heart", "liver", "lung"])
        blood_type = rand_bt()

    payload = {
        "recipient_id": rid,
        "organ_type": organ_type,
        "urgency": random.randint(1,5),
        "blood_type": blood_type,
        "status": "waiting",
    }
    post(f"{BASE}/needs", payload)


# -------------------------
# DONORS (50% MATCHABLE)
# -------------------------
print(f"=== Creating Donors ({COUNT}) ===")

donor_btypes = []
for i in range(COUNT):
    if i < COUNT // 2:
        # MATCHABLE donors match the recipients in first half
        donor_btypes.append(recipient_btypes[i])
    else:
        donor_btypes.append(rand_bt())

    result = post(f"{BASE}/donors", {
        "full_name": f"Donor {i}",
        "dob": rand_date(),
        "blood_type": donor_btypes[i],
        "status": "active",
    })
    if result and "id" in result:
        donor_ids.append(result["id"])


# -------------------------
# ORGANS (50% MATCHABLE)
# -------------------------
print(f"=== Creating Organs ({COUNT}) ===")

for i in range(COUNT):
    donor_id = donor_ids[i]

    if i < COUNT // 2:
        organ_type = "kidney"
    else:
        organ_type = rand_organ()

    payload = {
        "organ_type": organ_type,
        "condition": "good",
        "retrieved_at": rand_ts(),
        "donor_id": donor_id,
    }
    post(f"{BASE}/organs", payload)


# -------------------------
# CONSENTS
# -------------------------
print(f"=== Creating Consents ({COUNT}) ===")
for i in range(COUNT):
    did = donor_ids[i]
    payload = {
        "donor_id": did,
        "scope": [rand_organ()],
        "status": "signed",
    }
    post(f"{BASE}/consents", payload)

print("=== DONE ===")
