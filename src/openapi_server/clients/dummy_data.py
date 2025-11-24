#!/usr/bin/env python3
"""
Bulk Seeder using ONLY allowed POST routes under the Composite API
Guaranteed 50% matchable pairs
"""

import requests
import random
from datetime import datetime, timedelta

BASE = "https://composite-service-730071231868.us-central1.run.app"

HOSPITAL_COUNT = 4
COUNT = 50

def rand_date():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d")

def rand_ts():
    return (datetime.utcnow() - timedelta(days=random.randint(0, 2000))).isoformat()

def rand_bt():
    return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

def rand_organ():
    return random.choice(["kidney", "heart", "liver", "lung"])

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


hospital_ids = []
recipient_ids = []
donor_ids = []

# -----------------------------
# HOSPITALS
# -----------------------------
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

# -----------------------------
# RECIPIENTS
# -----------------------------
print(f"\n=== Creating Recipients ({COUNT}) ===")
recipient_btypes = []

for i in range(COUNT):
    bt = rand_bt()
    recipient_btypes.append(bt)

    result = post_debug(f"{BASE}/recipients", {
        "full_name": f"Recipient {i}",
        "dob": rand_date(),
        "blood_type": bt,
        "status": "active",
        "primary_hospital_id": random.choice(hospital_ids)
    })

    if result and "id" in result:
        recipient_ids.append(result["id"])

# -----------------------------
# NEEDS — 50% matchable
# -----------------------------
print(f"\n=== Creating Needs ({COUNT}) ===")

for i in range(COUNT):
    rid = recipient_ids[i]

    if i < COUNT // 2:
        organ_type = "kidney"
        blood_type = recipient_btypes[i]
    else:
        organ_type = rand_organ()
        blood_type = rand_bt()

    post_debug(f"{BASE}/recipients/{rid}/needs", {
        "organ_type": organ_type,
        "urgency": random.randint(1, 5),
        "blood_type": blood_type,
        "status": "waiting"
    })

# -----------------------------
# DONORS — 50% compatible
# -----------------------------
print(f"\n=== Creating Donors ({COUNT}) ===")

donor_btypes = []

for i in range(COUNT):
    if i < COUNT // 2:
        bt = recipient_btypes[i]
    else:
        bt = rand_bt()

    donor_btypes.append(bt)

    result = post_debug(f"{BASE}/donors", {
        "full_name": f"Donor {i}",
        "dob": rand_date(),
        "blood_type": bt,
        "status": "active"
    })

    if result and "id" in result:
        donor_ids.append(result["id"])

# -----------------------------
# ORGANS — 50% guaranteed kidney
# -----------------------------
print(f"\n=== Creating Organs ({COUNT}) ===")

for i in range(COUNT):
    did = donor_ids[i]

    organ_type = "kidney" if i < COUNT // 2 else rand_organ()

    post_debug(f"{BASE}/donors/{did}/organs", {
        "organ_type": organ_type,
        "condition": "good",
        "retrieved_at": rand_ts()
    })

# -----------------------------
# CONSENTS — correct statuses
# -----------------------------
print(f"\n=== Creating Consents ({COUNT}) ===")

for i in range(COUNT):
    did = donor_ids[i]

    post_debug(f"{BASE}/donors/{did}/consents", {
        "scope": [rand_organ()],
        "status": "granted"   # FIXED: valid enum
    })

print("\n=== DONE ===\n")

print("\n=== Creating Guaranteed Obvious Matches (10 pairs) ===")

GUARANTEED_COUNT = 10
guaranteed_donor_ids = []
guaranteed_recipient_ids = []
guaranteed_need_ids = []

for i in range(GUARANTEED_COUNT):

    # 1. Create a recipient with O+ blood (universal receiver for O)
    r = post_debug(f"{BASE}/recipients", {
        "full_name": f"Guaranteed Recipient {i}",
        "dob": rand_date(),
        "blood_type": "O+",
        "status": "active",
        "primary_hospital_id": random.choice(hospital_ids)
    })
    rid = r["id"]
    guaranteed_recipient_ids.append(rid)

    # 2. Create a need for kidney with O+ (guaranteed match for O donor)
    n = post_debug(f"{BASE}/recipients/{rid}/needs", {
        "organ_type": "kidney",
        "urgency": 5,
        "blood_type": "O+",
        "status": "waiting"
    })
    guaranteed_need_ids.append(n["id"])

    # 3. Create donor with O+ (universal donor)
    d = post_debug(f"{BASE}/donors", {
        "full_name": f"Guaranteed Donor {i}",
        "dob": rand_date(),
        "blood_type": "O+",
        "status": "active"
    })
    did = d["id"]
    guaranteed_donor_ids.append(did)

    # 4. Create a kidney organ for that donor
    post_debug(f"{BASE}/donors/{did}/organs", {
        "organ_type": "kidney",
        "condition": "perfect",
        "retrieved_at": rand_ts()
    })

    # 5. Create consent for kidney
    post_debug(f"{BASE}/donors/{did}/consents", {
        "scope": ["kidney"],
        "status": "granted"
    })
