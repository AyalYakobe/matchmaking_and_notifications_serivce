from fastapi import Response

@router.get(
    "/matches",
    responses={200: {"model": List[Match]}},
    summary="Get matches with pagination",
)
async def matches_get(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    donor_id: Optional[str] = Query(None),
    recipient_id: Optional[str] = Query(None),
):
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().matches_get(limit, offset, donor_id, recipient_id)

@router.get(
    "/matches/{id}",
    responses={
        200: {"model": Match, "description": "Match retrieved successfully"},
        404: {"description": "Match not found"},
    },
    tags=["matches"],
)
async def matches_id_get(id: StrictStr, response: Response):
    """Retrieve a specific match by ID with ETag and linked data."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")

    # Call the implementation (service) layer
    match = await BaseDefaultApi.subclasses[0]().matches_id_get(id)

    # Add an ETag header to enable client-side caching/version checking
    response.headers["ETag"] = f'W/"match-{id}-{match.status}"'

    # Add linked data (_links) for navigation
    match_dict = match.to_dict()
    match_dict["_links"] = {
        "self": f"/matches/{id}",
        "offers": f"/offers?matchId={id}",
        "donor": f"/donors/{match.donor_id}",
        "organ": f"/organs/{match.organ_id}",
    }

    return match_dict
