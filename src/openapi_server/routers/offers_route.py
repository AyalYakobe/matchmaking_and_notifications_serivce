# routers/offers_router.py

from fastapi import APIRouter, Response
from openapi_server.models.offer import Offer

from openapi_server.services.offers_service import (
    get_offers,
    create_offer,
)

router = APIRouter()


# ---------------------------------------------------------
# GET /offers (pagination + ETag + hypermedia)
# ---------------------------------------------------------
@router.get("/offers", response_model=list[Offer])
async def offers_get(limit: int = 10, offset: int = 0, response: Response = None):

    offers, etag = get_offers(limit, offset)

    # ETag
    response.headers["ETag"] = etag

    # Pagination header
    response.headers["Link"] = (
        f'</offers?limit={limit}&offset={offset + limit}>; rel="next"'
    )

    return offers


# ---------------------------------------------------------
# POST /offers (201 + Location + hypermedia)
# ---------------------------------------------------------
@router.post("/offers", response_model=Offer, status_code=201)
async def offers_post(offer: Offer, response: Response):

    new_offer = create_offer(offer)

    # Set the Location header
    response.headers["Location"] = f"/offers/{new_offer.id}"

    # Add hypermedia link
    return Offer(
        **new_offer.dict(),
        links={"self": f"/offers/{new_offer.id}"}
    )
