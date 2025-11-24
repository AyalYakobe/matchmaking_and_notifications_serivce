# coding: utf-8

"""
Matchmaking and Notification Service API
========================================

Entrypoint for the FastAPI microservice.

✔ Includes OpenAPI-generated routes
✔ Includes OffersService (DB-backed)
✔ Includes MatcherService for MS1/MS2 matching
✔ Passthrough endpoints for MS1 + MS2
✔ /match/do-match orchestration endpoint
✔ Cloud SQL DB test endpoint
"""

import requests
from fastapi import FastAPI

# OpenAPI-generated default routes
from openapi_server.apis.default_api import router as DefaultApiRouter

# Internal DB
from openapi_server.db.connection import get_connection

# MS1 + MS2 clients
from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client

# Matcher service (business logic)
from openapi_server.services.matcher_service import Matcher

# OffersService (DB-backed REST API)
from openapi_server.services.offers_service import router as OffersRouter



# ===============================================================
# 1. FASTAPI APP
# ===============================================================
app = FastAPI(
    title="Matchmaking and Notification Service API",
    version="1.0.0",
    description=(
        "This service orchestrates donor–recipient matching by calling MS1 "
        "(donors/organs) and MS2 (recipients/needs), performing matching logic, "
        "and providing a DB-backed Offers API."
    )
)



# ===============================================================
# 2. AUTO-GENERATED OPENAPI ROUTES
# ===============================================================
app.include_router(DefaultApiRouter)



# ===============================================================
# 3. CUSTOM SERVICES (Offers ONLY)
# ===============================================================
app.include_router(OffersRouter, prefix="/offers", tags=["Offers"])



# ===============================================================
# 4. Initialize MS1 + MS2 Clients + Matcher
# ===============================================================
COMPOSITE_BASE = "https://composite-service-730071231868.us-central1.run.app"

ms1 = MS1Client(COMPOSITE_BASE)
ms2 = MS2Client(COMPOSITE_BASE)
matcher = Matcher(COMPOSITE_BASE, COMPOSITE_BASE)



# ===============================================================
# 5. INTERNAL DB TEST
# ===============================================================
@app.get("/db-test-c")
def db_test_c():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE()")
    value = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"connected_to": value}



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
# 8. COMPOSITE SNAPSHOT
# ===============================================================
@app.get("/aggregate/full-snapshot")
def aggregate_full_snapshot():
    r = requests.get(f"{COMPOSITE_BASE}/snapshot/inventory")
    r.raise_for_status()
    return r.json()



# ===============================================================
# 9. MATCHMAKING ENDPOINT (BUSINESS LOGIC)
# ===============================================================
@app.post("/match/do-match")
def run_matching():
    """
    Perform donor-organ - recipient-need matching:
    - Fetch organs from MS1
    - Fetch needs from MS2
    - Match based on organ_type
    - DELETE consumed resources
    - Return match results (in-memory)
    """
    matches = matcher.match_and_consume()
    return {
        "match_count": len(matches),
        "matches": matches,
    }

