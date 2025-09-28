# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from openapi_server.models.match import Match
from openapi_server.models.matches_run_post_request import MatchesRunPostRequest
from openapi_server.models.offer import Offer
from openapi_server.models.offers_id_put_request import OffersIdPutRequest


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/health",
    responses={
        200: {"description": "OK"},
    },
    tags=["default"],
    summary="Health check",
    response_model_by_alias=True,
)
async def health_get(
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_get()


@router.get(
    "/matches",
    responses={
        200: {"model": List[Match], "description": "List of matches"},
    },
    tags=["default"],
    summary="Get matches filtered by donorId",
    response_model_by_alias=True,
)
async def matches_get(
    donor_id: Optional[StrictStr] = Query(None, description="", alias="donorId"),
) -> List[Match]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_get(donor_id)


@router.get(
    "/matches/{id}",
    responses={
        200: {"model": Match, "description": "Match found"},
    },
    tags=["default"],
    summary="Get a match by ID",
    response_model_by_alias=True,
)
async def matches_id_get(
    id: StrictStr = Path(..., description=""),
) -> Match:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_id_get(id)


@router.post(
    "/matches:run",
    responses={
        200: {"model": Match, "description": "Match results"},
    },
    tags=["default"],
    summary="Run matching for a donor or organ",
    response_model_by_alias=True,
)
async def matches_run_post(
    matches_run_post_request: MatchesRunPostRequest = Body(None, description=""),
) -> Match:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_run_post(matches_run_post_request)


@router.put(
    "/offers/{id}",
    responses={
        200: {"model": Offer, "description": "Offer updated"},
    },
    tags=["default"],
    summary="Update offer status",
    response_model_by_alias=True,
)
async def offers_id_put(
    id: StrictStr = Path(..., description=""),
    offers_id_put_request: OffersIdPutRequest = Body(None, description=""),
) -> Offer:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_id_put(id, offers_id_put_request)


@router.post(
    "/offers",
    responses={
        201: {"model": Offer, "description": "Offer created"},
    },
    tags=["default"],
    summary="Create an allocation offer",
    response_model_by_alias=True,
)
async def offers_post(
    offer: Offer = Body(None, description=""),
) -> Offer:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_post(offer)
