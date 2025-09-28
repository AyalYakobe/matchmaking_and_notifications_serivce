# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictStr  # noqa: F401
from typing import Any, List, Optional  # noqa: F401
from openapi_server.models.match import Match  # noqa: F401
from openapi_server.models.matches_run_post_request import MatchesRunPostRequest  # noqa: F401
from openapi_server.models.offer import Offer  # noqa: F401
from openapi_server.models.offers_id_put_request import OffersIdPutRequest  # noqa: F401


def test_health_get(client: TestClient):
    """Test case for health_get

    Health check
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/health",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_matches_get(client: TestClient):
    """Test case for matches_get

    Get matches filtered by donorId
    """
    params = [("donor_id", 'donor_id_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/matches",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_matches_id_get(client: TestClient):
    """Test case for matches_id_get

    Get a match by ID
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/matches/{id}".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_matches_run_post(client: TestClient):
    """Test case for matches_run_post

    Run matching for a donor or organ
    """
    matches_run_post_request = openapi_server.MatchesRunPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/matches:run",
    #    headers=headers,
    #    json=matches_run_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_offers_id_put(client: TestClient):
    """Test case for offers_id_put

    Update offer status
    """
    offers_id_put_request = openapi_server.OffersIdPutRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/offers/{id}".format(id='id_example'),
    #    headers=headers,
    #    json=offers_id_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_offers_post(client: TestClient):
    """Test case for offers_post

    Create an allocation offer
    """
    offer = {"id":"id","match_id":"matchId","status":"pending"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/offers",
    #    headers=headers,
    #    json=offer,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

