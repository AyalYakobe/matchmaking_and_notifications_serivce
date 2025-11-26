# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any, List
from openapi_server.models.health_get200_response import HealthGet200Response
from openapi_server.models.health_post_request import HealthPostRequest
from openapi_server.models.health_put_request import HealthPutRequest
from openapi_server.models.match import Match
from openapi_server.models.offer import Offer


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def health_delete(
        self,
    ) -> None:
        """Delete or reset simulated health state."""
        ...


    async def health_get(
        self,
    ) -> HealthGet200Response:
        """Retrieve API health status."""
        ...


    async def health_post(
        self,
        health_post_request: HealthPostRequest,
    ) -> None:
        """Send custom health status for testing."""
        ...


    async def health_put(
        self,
        health_put_request: HealthPutRequest,
    ) -> None:
        """Update simulated health configuration."""
        ...


    async def matches_delete(
        self,
    ) -> None:
        """Delete all matches (for demonstration purposes)."""
        ...


    async def matches_get(
        self,
    ) -> List[Match]:
        """Retrieve a list of all matches."""
        ...


    async def matches_id_delete(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def matches_id_get(
        self,
        id: StrictStr,
    ) -> Match:
        ...


    async def matches_id_post(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def matches_id_put(
        self,
        id: StrictStr,
        match: Match,
    ) -> None:
        ...


    async def matches_post(
        self,
        match: Match,
    ) -> Match:
        """Add a new donor-organ match."""
        ...


    async def matches_put(
        self,
        match: List[Match],
    ) -> None:
        """Update multiple matches (for demonstration purposes)."""
        ...


    async def offers_delete(
        self,
    ) -> None:
        """Delete all offers (for demonstration purposes)."""
        ...


    async def offers_get(
        self,
    ) -> List[Offer]:
        """Retrieve a list of all offers."""
        ...


    async def offers_id_delete(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def offers_id_get(
        self,
        id: StrictStr,
    ) -> Offer:
        ...


    async def offers_id_post(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def offers_id_put(
        self,
        id: StrictStr,
        offer: Offer,
    ) -> None:
        ...


    async def offers_post(
        self,
        offer: Offer,
    ) -> None:
        """Add a new allocation offer."""
        ...


    async def offers_put(
        self,
        offer: List[Offer],
    ) -> None:
        """Update several offers at once (for demonstration purposes)."""
        ...
