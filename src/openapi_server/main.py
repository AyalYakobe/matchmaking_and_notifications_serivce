# coding: utf-8

"""
Matchmaking and Notification Service API
========================================
Entrypoint for the FastAPI microservice.
"""

import requests
from fastapi import FastAPI

from openapi_server.db.connection import get_connection
from openapi_server.routers.matches_route import router as MatchesRouter
from openapi_server.routers.offers_route import router as OffersRouter
from openapi_server.routers.ms_composite_route import router as CompositeRouter


# ===============================================================
# FASTAPI APP
# ===============================================================
app = FastAPI(
    title="Matchmaking and Notification Service API",
    version="1.0.0",
    description="Donor–recipient matching system orchestrating MS1 and MS2 with DB-backed matches & offers.",
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


app.include_router(CompositeRouter)
app.include_router(MatchesRouter)
app.include_router(OffersRouter, tags=["Offers"])

