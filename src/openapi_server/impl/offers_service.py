import hashlib
import json
from fastapi import Response, HTTPException
from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.offer import Offer

OFFERS = {}

class OffersService(BaseDefaultApi):
    async def offers_get(self, limit, offset, response: Response):
        offers = list(OFFERS.values())[offset: offset + limit]
        body = json.dumps([o.dict() for o in offers])
        etag = hashlib.sha1(body.encode()).hexdigest()

        response.headers["ETag"] = etag
        response.headers["Link"] = f'</offers?limit={limit}&offset={offset+limit}>; rel="next"'

        return offers

    async def offers_post(self, offer: Offer, response: Response):
        new_id = f"offer-{len(OFFERS) + 1}"
        offer.id = new_id
        OFFERS[new_id] = offer

        response.status_code = 201
        response.headers["Location"] = f"/offers/{new_id}"
        return Offer(**offer.dict(), links={"self": f"/offers/{new_id}"})
