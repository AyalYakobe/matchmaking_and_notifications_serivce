# coding: utf-8

"""
Matchmaking and Notification Service API
========================================
Entrypoint for the FastAPI microservice.
"""

import requests
from fastapi import FastAPI

# Internal DB
from openapi_server.db.connection import get_connection

# Matcher service (business logic)
from openapi_server.services.matcher_service import Matcher

# Routers
from openapi_server.routers.matches_route import router as MatchesRouter
from openapi_server.routers.offers_route import router as OffersRouter
from openapi_server.routers.ms_composite_route import router as CompositeRouter


# ===============================================================
# FASTAPI APP
# ===============================================================
app = FastAPI(
    title="Matchmaking and Notification Service API",
    version="1.0.0",
    description="Orchestrates donor–recipient matching and provides DB-backed Offers + Matches APIs."
)

# ===============================================================
# HEALTH CHECK
# ===============================================================
@app.get("/db-test-c", tags=["Health"])
def db_test_c():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE()")
    value = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"connected_to": value}


# ===============================================================
# MATCHMAKING ENDPOINT (BUSINESS LOGIC)
# ===============================================================
@app.post("/match/do-match", tags=["Matches"])
def run_matching():
    """
    Perform donor-organ <-> recipient-need matching:
    - Fetch organs from MS1
    - Fetch needs from MS2
    - Match based on organ_type + blood-type compatibility
    - Save match + create offer
    - Publish Pub/Sub event
    - Delete consumed resources
    """
    matches = matcher.match_and_consume()
    return {
        "match_count": len(matches),
        "matches": matches,
    }


# ===============================================================
# INCLUDE ROUTERS
# ===============================================================
app.include_router(CompositeRouter)
app.include_router(MatchesRouter)
app.include_router(OffersRouter, tags=["Offers"])
