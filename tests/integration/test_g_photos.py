"""Integration test cases for the g_photos route."""

import json
import os
from http import HTTPStatus
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {
        "username": os.getenv("ADMIN_USERNAME"),
        "role": "admin",
        "exp": 9999999999,
    }
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def g_photo() -> dict:
    """Test g_mediaitem return object for testing."""
    file_path = Path("tests/files/g_mediaitem.json")
    with file_path.open() as file:
        return json.load(file)


@pytest.mark.integration
def test_get_g_photos(
    client: TestClient, mocker: MockFixture, token: str, g_photo: dict
) -> None:
    """Should return OK, and a body with mediaItems."""
    mocker.patch(
        "app.services.google_photos_service.GooglePhotosService.get_media_items",
        return_value=g_photo,
    )
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.get("/g_photos", headers=headers)
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(g_photo) is dict
    assert len(body["mediaItems"]) == 1


@pytest.mark.integration
def test_get_g_photos_by_album(
    client: TestClient, mocker: MockFixture, token: str, g_photo: dict
) -> None:
    """Test get a body with mediaItems."""
    mocker.patch(
        "app.services.google_photos_service.GooglePhotosService.get_media_items",
        return_value=g_photo,
    )
    album_id = (
        "APU9jkgGi39m2nO7a0H9IhR5t-ZyCQbayNEC_lb1UjK_8DbyD8WJDhPz6g-TJ9-O02DlhPW4PDRP"
    )
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.get(f"/g_photos/{album_id}", headers=headers)
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(g_photo) is dict
    assert len(body["mediaItems"]) == 1
