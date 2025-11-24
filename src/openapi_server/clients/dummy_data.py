#!/usr/bin/env python3
"""
Bulk Data Seeder for MS1 + MS2 via Composite API
Uses ONLY legal POST routes based on OpenAPI
"""

import requests
import random
from datetime import datetime, timedelta

BASE = "https://composite-service-730071231868.us-central1.run.app"

HOSPITAL_COUNT = 4
COUNT = 50

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_date():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d")

def rand_ts():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).isoformat()

def rand_bt():
    return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

def rand_organ():
    return random.choice(["kidney", "heart", "liver", "lung"])

# ---------------------------------------------------------------------------
# Debug POST helper
# ---------------------------------------------------------------------------

def post_debug(url, payload):
    print("\n---------------------------------------")
    print(f"POST → {url}")
    print(f"Payload: {payload}")

    try:
        r = requests.post(url, json=payload)
    except Exception as e:
        print("❌ REQUEST FAILED:", e)
        return None

    print(f"Status: {r.status_code}")

    if r.status_code >= 300:
        print("❌ ERROR BODY:", r.text)
        return None

    try:
        data = r.json()
        print("Response JSON:", data)
        return data
    except:
        print("❌ JSON PARSE ERROR:", r.text)
        return None


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

hospital_ids = []
recipient_ids = []
donor_ids = []


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

print(f"\n=== Creating Hospitals ({HOSPITAL_COUNT}) ===")
for i in range(HOSPITAL_COUNT):
    result = post_debug(f"{BASE}/hospitals", {
        "name": f"Hospital {i}",
        "city": "CityX",
        "state": "StateY",
        "phone": "555-555-5555",
        "status": "active"
    })
    if result and "id" in result:
        hospital_ids.append(result["id"])


print(f"\n=== Creating Recipients ({COUNT}) ===")
recipient_btypes = []
for i in range(COUNT):
    b = rand_bt()
    recipient_btypes.append(b)

    result = post_debug(f"{BASE}/recipients", {
        "full_name": f"Recipient {i}",
        "dob": rand_date(),
        "blood_type": b,
        "status": "active",
        "primary_hospital_id": random.choice(hospital_ids)
    })
    if result and "id" in result:
        recipient_ids.append(result["id"])


print(f"\n=== Creating Needs ({COUNT}) via /recipients/<id>/needs ===")
for i in range(COUNT):
    rid = recipient_ids[i]

    organ_type = "kidney" if i < COUNT // 2 else rand_organ()

    post_debug(f"{BASE}/recipients/{rid}/needs", {
        "organ_type": organ_type,
        "urgency": random.randint(1, 5),
        "blood_type": recipient_btypes[i],
        "status": "waiting"
    })


print(f"\n=== Creating Donors ({COUNT}) ===")
donor_btypes = []
for i in range(COUNT):
    if i < COUNT // 2:
        donor_btypes.append(recipient_btypes[i])
    else:
        donor_btypes.append(rand_bt())

    result = post_debug(f"{BASE}/donors", {
        "full_name": f"Donor {i}",
        "dob": rand_date(),
        "blood_type": donor_btypes[i],
        "status": "active"
    })
    if result and "id" in result:
        donor_ids.append(result["id"])


print(f"\n=== Creating Organs ({COUNT}) via /donors/<id>/organs ===")
for i in range(COUNT):
    did = donor_ids[i]
    organ_type = "kidney" if i < COUNT // 2 else rand_organ()

    post_debug(f"{BASE}/donors/{did}/organs", {
        "organ_type": organ_type,
        "condition": "good",
        "retrieved_at": rand_ts()
    })


print(f"\n=== Creating Consents ({COUNT}) via /donors/<id>/consents ===")
for i in range(COUNT):
    did = donor_ids[i]

    post_debug(f"{BASE}/donors/{did}/consents", {
        "scope": [rand_organ()],
        "status": "signed"
    })


print("\n=== DONE ===\n")
