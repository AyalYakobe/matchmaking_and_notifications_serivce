# coding: utf-8

"""
Matchmaking and Notification Service API
========================================

This file defines the FastAPI application entrypoint.

✔ Includes OpenAPI-generated routes
✔ Exposes MS1 passthrough endpoints
✔ Exposes MS2 passthrough endpoints
✔ Adds a /match/do-match orchestration endpoint
✔ Includes DB test endpoint

Clients:
- MS1Client (donors, organs, consents)
- MS2Client (recipients, needs, hospitals)
- Matcher (business logic matching organ ↔ need)
"""
from fastapi import FastAPI
from openapi_server.apis.default_api import router as DefaultApiRouter

# Internal DB
from openapi_server.db.connection import get_connection

# Clients for MS1 + MS2
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client

# Matcher service
from openapi_server.services.matcher import Matcher


# ===============================================================
# 1. Create FastAPI application instance
# ===============================================================
app = FastAPI(
    title="Matchmaking and Notification Service API",
    description=(
        "Microservice that orchestrates donor–recipient matching by "
        "fetching data from MS1 (donors/organs) and MS2 (recipients/needs), "
        "performing matching logic, and removing consumed resources."
    ),
    version="1.0.0",
)


# ===============================================================
# 2. Register OpenAPI-generated routes
# ===============================================================
app.include_router(DefaultApiRouter)


# ===============================================================
# 3. Initialize MS1 + MS2 Clients + Matcher
# ===============================================================

COMPOSITE_BASE = "https://composite-service-730071231868.us-central1.run.app"

ms1 = MS1Client(COMPOSITE_BASE)
ms2 = MS2Client(COMPOSITE_BASE)
matcher = Matcher(COMPOSITE_BASE, COMPOSITE_BASE)

# ===============================================================
# 4. INTERNAL: DB TEST ENDPOINT
# ===============================================================
@app.get("/db-test-c")
def db_test_c():
    """Test connection to Cloud SQL."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE()")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return {"connected_to": row[0]}


# ===============================================================
# 5. MS1: Donor Registry Passthrough Endpoints
# ===============================================================

@app.get("/ms1/health")
def ms1_health():
    return ms1.list_donors()  # or ms1.health() if implemented


# --- Donors ---
@app.get("/ms1/donors")
def ms1_list_donors():
    return ms1.list_donors()


@app.get("/ms1/donors/{donor_id}")
def ms1_get_donor(donor_id: str):
    return ms1.get_donor(donor_id)


@app.get("/ms1/donors/{donor_id}/organs")
def ms1_organs_for_donor(donor_id: str):
    return ms1.list_organs_for_donor(donor_id)


# --- Organs ---
@app.get("/ms1/organs")
def ms1_list_organs():
    return ms1.list_organs()


# --- Consents ---
@app.get("/ms1/consents")
def ms1_list_consents():
    return ms1.list_consents()


@app.get("/ms1/consents/{consent_id}")
def ms1_get_consent(consent_id: str):
    return ms1.get_consent(consent_id)


@app.get("/ms1/all")
def ms1_all():
    return {
        "donors": ms1.list_donors(),
        "organs": ms1.list_organs(),
        "consents": ms1.list_consents(),
    }


# ===============================================================
# 6. MS2: Recipient Registry Passthrough Endpoints
# ===============================================================

# --- Recipients ---
@app.get("/ms2/recipients")
def ms2_list_recipients():
    return ms2.list_recipients()


@app.get("/ms2/recipients/{recipient_id}")
def ms2_get_recipient(recipient_id: str):
    return ms2.get_recipient(recipient_id)


@app.get("/ms2/recipients/{recipient_id}/needs")
def ms2_needs_for_recipient(recipient_id: str):
    return ms2.list_needs_for_recipient(recipient_id)


# --- Needs ---
@app.get("/ms2/needs")
def ms2_list_needs():
    return ms2.list_needs()


@app.get("/ms2/needs/{need_id}")
def ms2_get_need(need_id: str):
    return ms2.get_need(need_id)


# --- Hospitals ---
@app.get("/ms2/hospitals")
def ms2_list_hospitals():
    return ms2.list_hospitals()


@app.get("/ms2/hospitals/{hospital_id}")
def ms2_get_hospital(hospital_id: str):
    return ms2.get_hospital(hospital_id)


@app.get("/ms2/all")
def ms2_all():
    return {
        "recipients": ms2.list_recipients(),
        "needs": ms2.list_needs(),
        "hospitals": ms2.list_hospitals(),
    }


# ===============================================================
# 7. Composite “Aggregate” Endpoint
# ===============================================================
import requests

@app.get("/aggregate/full-snapshot")
def aggregate_full_snapshot():
    url = f"{COMPOSITE_BASE}/snapshot/inventory"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

# ===============================================================
# 8. MATCHMAKING ENDPOINT — CORE BUSINESS LOGIC
# ===============================================================
@app.post("/match/do-match")
def run_matching():
    """
    Perform donor-organ ↔ recipient-need matching.

    For each organ:
      - Find compatible need
      - Create a match record (in-memory return for now)
      - DELETE organ (MS1)
      - DELETE need (MS2)

    Returns:
        List of matches created.
    """
    matches = matcher.match_and_consume()
    return {
        "match_count": len(matches),
        "matches": matches,
    }
