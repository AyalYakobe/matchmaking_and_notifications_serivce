# src/openapi_server/routers/matches_route.py

from fastapi import APIRouter, HTTPException

from openapi_server.services.matches_service import (
    list_matches as svc_list_matches,
    get_full_match as svc_get_full_match,
)

router = APIRouter()


# ===============================================================
# GET /internal/matches
# ===============================================================
@router.get("/internal/matches", tags=["Matches"])
def list_matches():
    return svc_list_matches()


# ===============================================================
# GET /matches/{match_id}/full
# ===============================================================
@router.get("/matches/{match_id}/full", tags=["Matches"])
def get_full_match(match_id: int):
    result = svc_get_full_match(match_id)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

    return result
