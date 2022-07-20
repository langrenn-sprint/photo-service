"""Integration test cases for the g_photos route."""
import json
import os

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
import jwt
import pytest
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": os.getenv("ADMIN_USERNAME"), "roles": ["admin"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
def token_unsufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": "user", "roles": ["user"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
async def g_photo() -> dict:
    """An g_mediaitem return object for testing."""
    with open("tests/files/g_mediaitem.json", "r") as file:
        response = json.load(file)

    return response


@pytest.mark.integration
async def test_get_g_photos(
    client: _TestClient, mocker: MockFixture, token: MockFixture, g_photo: dict
) -> None:
    """Should return OK, and a body with mediaItems."""
    mocker.patch(
        "photo_service.services.google_photos_service.GooglePhotosService.get_media_items",
        return_value=g_photo,
    )
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get("/g_photos", headers=headers)
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(g_photo) is dict
        assert len(body["mediaItems"]) == 1


@pytest.mark.integration
async def test_get_g_photos_by_album(
    client: _TestClient, mocker: MockFixture, token: MockFixture, g_photo: dict
) -> None:
    """Should return OK, and a body with mediaItems."""
    mocker.patch(
        "photo_service.services.google_photos_service.GooglePhotosService.get_media_items",
        return_value=g_photo,
    )
    albumId = (
        "APU9jkgGi39m2nO7a0H9IhR5t-ZyCQbayNEC_lb1UjK_8DbyD8WJDhPz6g-TJ9-O02DlhPW4PDRP"
    )
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get(f"/g_photos/{albumId}", headers=headers)
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(g_photo) is dict
        assert len(body["mediaItems"]) == 1
