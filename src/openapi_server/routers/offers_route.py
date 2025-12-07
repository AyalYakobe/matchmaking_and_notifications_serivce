# src/openapi_server/routers/offers_route.py

from fastapi import APIRouter, Response, HTTPException
from typing import List

from openapi_server.models.offer import Offer, OfferCreate, OfferUpdate
from openapi_server.services.offers_service import (
    get_offers,
    create_offer,
    get_offer,
    update_offer,
    delete_offer,
)

router = APIRouter()


# ---------------------------------------------------------
# GET /offers  (ETag + pagination)
# ---------------------------------------------------------
@router.get("/offers", response_model=List[Offer], tags=["Offers"])
async def offers_get(limit: int = 10, offset: int = 0, response: Response = None):

    offers, etag = await get_offers(limit, offset)

    # ETag header
    if etag:
        response.headers["ETag"] = etag

    # Pagination Link header (relative path)
    response.headers["Link"] = (
        f'</offers?limit={limit}&offset={offset + limit}>; rel="next"'
    )

    return offers


# ---------------------------------------------------------
# POST /offers  (201 Created + Location header)
# ---------------------------------------------------------
@router.post(
    "/offers",
    response_model=Offer,
    status_code=201,
    response_model_exclude_unset=True,
    tags=["Offers"]
)
async def offers_post(offer: OfferCreate, response: Response):

    new_offer = await create_offer(offer)

    # REST: 201 Created → include Location header pointing to the *new resource*
    resource_path = f"/offers/{new_offer.id}"
    response.headers["Location"] = resource_path

    # Optional but recommended by some REST guidelines
    response.headers["Content-Location"] = resource_path

    return new_offer


# ---------------------------------------------------------
# GET /offers/{offer_id}
# ---------------------------------------------------------
@router.get("/offers/{offer_id}", response_model=Offer, tags=["Offers"])
async def offers_get_one(offer_id: int):

    offer = await get_offer(offer_id)

    if offer is None:
        raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

    return offer


# ---------------------------------------------------------
# PUT/PATCH /offers/{offer_id}
# ---------------------------------------------------------
@router.put("/offers/{offer_id}", response_model=Offer, tags=["Offers"])
@router.patch("/offers/{offer_id}", response_model=Offer, tags=["Offers"])
async def offers_update(offer_id: int, payload: OfferUpdate):

    updated = await update_offer(offer_id, payload)

    if updated is None:
        raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

    return updated


# ---------------------------------------------------------
# DELETE /offers/{offer_id}
# ---------------------------------------------------------
@router.delete("/offers/{offer_id}", status_code=204, tags=["Offers"])
async def offers_delete(offer_id: int):

    ok = await delete_offer(offer_id)

    if not ok:
        raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

    return
