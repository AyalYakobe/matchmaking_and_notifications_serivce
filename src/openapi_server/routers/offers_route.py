# routers/offers_router.py

from fastapi import APIRouter, Response
from openapi_server.models.offer import Offer
from openapi_server.services.offers_service import get_offers, create_offer

router = APIRouter()

# ---------------------------------------------------------
# GET /offers  (ETag + pagination)
# ---------------------------------------------------------
@router.get("/offers", response_model=list[Offer])
async def offers_get(limit: int = 10, offset: int = 0, response: Response = None):

    offers, etag = await get_offers(limit, offset)

    # ETag header
    if etag:
        response.headers["ETag"] = etag

    # Pagination header
    response.headers["Link"] = (
        f'</offers?limit={limit}&offset={offset + limit}>; rel="next"'
    )

    return offers


# ---------------------------------------------------------
# POST /offers  (201 Created + Location header)
# ---------------------------------------------------------
@router.post("/offers", response_model=Offer, status_code=201)
async def offers_post(offer: Offer, response: Response):

    new_offer = await create_offer(offer)

    # REST: Created → include Location header
    response.headers["Location"] = f"/offers/{new_offer.id}"

    return new_offer
