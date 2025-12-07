# src/openapi_server/routers/matches_route.py

from fastapi import APIRouter, HTTPException
from typing import List

from openapi_server.models.match_model import Match, MatchCreate, MatchUpdate
from openapi_server.services.matcher_service import (
    list_matches,
    create_match,
    get_match,
    update_match,
    delete_match,
    get_full_match,
)

router = APIRouter()


# ===============================================================
# GET /matches - list
# ===============================================================
@router.get("/matches", response_model=List[Match], tags=["Matches"])
def route_list_matches():
    return list_matches()


# ===============================================================
# POST /matches - create
# ===============================================================
@router.post("/matches", response_model=Match, status_code=201, tags=["Matches"])
def route_create_match(payload: MatchCreate):
    return create_match(payload)


# ===============================================================
# GET /matches/{match_id} - retrieve
# ===============================================================
@router.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_get_match(match_id: str):
    match = get_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match


# ===============================================================
# PUT/PATCH /matches/{match_id} - update
# ===============================================================
@router.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
@router.patch("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_update_match(match_id: str, payload: MatchUpdate):
    updated = update_match(match_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return updated


# ===============================================================
# DELETE /matches/{match_id}
# ===============================================================
@router.delete("/matches/{match_id}", status_code=204, tags=["Matches"])
def route_delete_match(match_id: str):
    ok = delete_match(match_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return


# ===============================================================
# GET /matches/{match_id}/full (existing)
# ===============================================================
@router.get("/matches/{match_id}/full", tags=["Matches"])
def route_get_full_match(match_id: str):
    result = get_full_match(match_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return result
