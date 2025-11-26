# coding: utf-8
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, Response
from pydantic import StrictStr
from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.health_get200_response import HealthGet200Response
from openapi_server.models.health_post_request import HealthPostRequest
from openapi_server.models.health_put_request import HealthPutRequest
from openapi_server.models.match import Match
from openapi_server.models.offer import Offer
from openapi_server.services.jobs_service import start_job, get_job_status


router = APIRouter()

# ---------------- HEALTH ----------------
@router.get("/health", response_model=HealthGet200Response, tags=["default"])
async def health_get():
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_get()


# ---------------- MATCHES ----------------
@router.get("/matches", response_model=List[Match], tags=["matches"])
async def matches_get(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    donor_id: Optional[str] = Query(None),
    recipient_id: Optional[str] = Query(None),
    response: Response = None,
):
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_get(limit, offset, donor_id, recipient_id, response)


@router.get("/matches/{id}", response_model=Match, tags=["matches"])
async def matches_id_get(id: StrictStr, response: Response):
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")

    match = await BaseDefaultApi.subclasses[0]().matches_id_get(id)
    response.headers["ETag"] = f'W/"match-{id}-{match.status}"'
    match_dict = match.to_dict()
    match_dict["_links"] = {
        "self": f"/matches/{id}",
        "offers": f"/offers?matchId={id}",
        "donor": f"/donors/{match.donor_id}",
        "organ": f"/organs/{match.organ_id}",
    }
    return match_dict


# ---------------- JOBS ----------------
@router.post("/jobs", tags=["jobs"])
async def start_async_job(response: Response):
    job_id = await start_job()
    response.status_code = 202
    response.headers["Location"] = f"/jobs/{job_id}"
    return {"jobId": job_id, "status": "pending"}


@router.get("/jobs/{job_id}", tags=["jobs"])
async def get_job(job_id: str, response: Response):
    job = await get_job_status(job_id)
    response.status_code = 200 if job["status"] == "done" else 202
    return job
