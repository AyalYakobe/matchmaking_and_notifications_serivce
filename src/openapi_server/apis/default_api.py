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
from typing import Any, List
from openapi_server.models.health_get200_response import HealthGet200Response
from openapi_server.models.health_post_request import HealthPostRequest
from openapi_server.models.health_put_request import HealthPutRequest
from openapi_server.models.match import Match
from openapi_server.models.offer import Offer


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/health",
    responses={
        204: {"description": "Health data reset successfully"},
    },
    tags=["default"],
    summary="Reset health data",
    response_model_by_alias=True,
)
async def health_delete(
) -> None:
    """Delete or reset simulated health state."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_delete()


@router.get(
    "/health",
    responses={
        200: {"model": HealthGet200Response, "description": "Service is healthy"},
    },
    tags=["default"],
    summary="Health check",
    response_model_by_alias=True,
)
async def health_get(
) -> HealthGet200Response:
    """Retrieve API health status."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_get()


@router.post(
    "/health",
    responses={
        201: {"description": "Health status recorded"},
    },
    tags=["default"],
    summary="Report custom health status",
    response_model_by_alias=True,
)
async def health_post(
    health_post_request: HealthPostRequest = Body(None, description=""),
) -> None:
    """Send custom health status for testing."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_post(health_post_request)


@router.put(
    "/health",
    responses={
        200: {"description": "Health configuration updated"},
    },
    tags=["default"],
    summary="Update health configuration",
    response_model_by_alias=True,
)
async def health_put(
    health_put_request: HealthPutRequest = Body(None, description=""),
) -> None:
    """Update simulated health configuration."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().health_put(health_put_request)


@router.delete(
    "/matches",
    responses={
        204: {"description": "All matches deleted"},
    },
    tags=["default"],
    summary="Delete all matches",
    response_model_by_alias=True,
)
async def matches_delete(
) -> None:
    """Delete all matches (for demonstration purposes)."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_delete()


@router.get(
    "/matches",
    responses={
        200: {"model": List[Match], "description": "A list of matches"},
    },
    tags=["default"],
    summary="Get all matches",
    response_model_by_alias=True,
)
async def matches_get(
) -> List[Match]:
    """Retrieve a list of all matches."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_get()


@router.delete(
    "/matches/{id}",
    responses={
        204: {"description": "Match deleted successfully"},
        404: {"description": "Match not found"},
    },
    tags=["default"],
    summary="Delete a specific match",
    response_model_by_alias=True,
)
async def matches_id_delete(
    id: StrictStr = Path(..., description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_id_delete(id)


@router.get(
    "/matches/{id}",
    responses={
        200: {"model": Match, "description": "Match retrieved successfully"},
        404: {"description": "Match not found"},
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
    "/matches/{id}",
    responses={
        201: {"description": "Match reprocessed successfully"},
    },
    tags=["default"],
    summary="Duplicate or reprocess a specific match",
    response_model_by_alias=True,
)
async def matches_id_post(
    id: StrictStr = Path(..., description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_id_post(id)


@router.put(
    "/matches/{id}",
    responses={
        200: {"description": "Match updated successfully"},
        404: {"description": "Match not found"},
    },
    tags=["default"],
    summary="Update a specific match",
    response_model_by_alias=True,
)
async def matches_id_put(
    id: StrictStr = Path(..., description=""),
    match: Match = Body(None, description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_id_put(id, match)


@router.post(
    "/matches",
    responses={
        201: {"model": Match, "description": "Match created successfully"},
    },
    tags=["default"],
    summary="Create a new match",
    response_model_by_alias=True,
)
async def matches_post(
    match: Match = Body(None, description=""),
) -> Match:
    """Add a new donor-organ match."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_post(match)


@router.put(
    "/matches",
    responses={
        200: {"description": "Matches updated successfully"},
    },
    tags=["default"],
    summary="Update all matches (bulk operation placeholder)",
    response_model_by_alias=True,
)
async def matches_put(
    match: List[Match] = Body(None, description=""),
) -> None:
    """Update multiple matches (for demonstration purposes)."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_put(match)


@router.delete(
    "/offers",
    responses={
        204: {"description": "All offers deleted"},
    },
    tags=["default"],
    summary="Delete all offers",
    response_model_by_alias=True,
)
async def offers_delete(
) -> None:
    """Delete all offers (for demonstration purposes)."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_delete()


@router.get(
    "/offers",
    responses={
        200: {"model": List[Offer], "description": "A list of offers"},
    },
    tags=["default"],
    summary="Get all offers",
    response_model_by_alias=True,
)
async def offers_get(
) -> List[Offer]:
    """Retrieve a list of all offers."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_get()


@router.delete(
    "/offers/{id}",
    responses={
        204: {"description": "Offer deleted successfully"},
        404: {"description": "Offer not found"},
    },
    tags=["default"],
    summary="Delete an offer by ID",
    response_model_by_alias=True,
)
async def offers_id_delete(
    id: StrictStr = Path(..., description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_id_delete(id)


@router.get(
    "/offers/{id}",
    responses={
        200: {"model": Offer, "description": "Offer retrieved successfully"},
        404: {"description": "Offer not found"},
    },
    tags=["default"],
    summary="Get an offer by ID",
    response_model_by_alias=True,
)
async def offers_id_get(
    id: StrictStr = Path(..., description=""),
) -> Offer:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_id_get(id)


@router.post(
    "/offers/{id}",
    responses={
        201: {"description": "Offer duplicated successfully"},
    },
    tags=["default"],
    summary="Duplicate or resend a specific offer",
    response_model_by_alias=True,
)
async def offers_id_post(
    id: StrictStr = Path(..., description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_id_post(id)


@router.put(
    "/offers/{id}",
    responses={
        200: {"description": "Offer updated successfully"},
        404: {"description": "Offer not found"},
    },
    tags=["default"],
    summary="Update an offer by ID",
    response_model_by_alias=True,
)
async def offers_id_put(
    id: StrictStr = Path(..., description=""),
    offer: Offer = Body(None, description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_id_put(id, offer)


@router.post(
    "/offers",
    responses={
        201: {"description": "Offer created successfully"},
    },
    tags=["default"],
    summary="Create a new offer",
    response_model_by_alias=True,
)
async def offers_post(
    offer: Offer = Body(None, description=""),
) -> None:
    """Add a new allocation offer."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_post(offer)


@router.put(
    "/offers",
    responses={
        200: {"description": "Offers updated successfully"},
    },
    tags=["default"],
    summary="Update multiple offers (bulk operation placeholder)",
    response_model_by_alias=True,
)
async def offers_put(
    offer: List[Offer] = Body(None, description=""),
) -> None:
    """Update several offers at once (for demonstration purposes)."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().offers_put(offer)
