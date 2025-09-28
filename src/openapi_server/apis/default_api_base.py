# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any, List, Optional
from openapi_server.models.match import Match
from openapi_server.models.matches_run_post_request import MatchesRunPostRequest
from openapi_server.models.offer import Offer
from openapi_server.models.offers_id_put_request import OffersIdPutRequest


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def health_get(
        self,
    ) -> None:
        ...


    async def matches_get(
        self,
        donor_id: Optional[StrictStr],
    ) -> List[Match]:
        ...


    async def matches_id_get(
        self,
        id: StrictStr,
    ) -> Match:
        ...


    async def matches_run_post(
        self,
        matches_run_post_request: MatchesRunPostRequest,
    ) -> Match:
        ...


    async def offers_id_put(
        self,
        id: StrictStr,
        offers_id_put_request: OffersIdPutRequest,
    ) -> Offer:
        ...


    async def offers_post(
        self,
        offer: Offer,
    ) -> Offer:
        ...
