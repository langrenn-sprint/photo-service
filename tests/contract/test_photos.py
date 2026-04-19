"""Contract test cases for photos."""

import logging
import os
from collections.abc import AsyncGenerator
from copy import deepcopy
from http import HTTPStatus
from typing import Any

import httpx
import motor.motor_asyncio
import pytest
from pytest_mock import MockFixture

from app.utils import db_utils

USERS_HOST_SERVER = os.getenv("USERS_HOST_SERVER")
USERS_HOST_PORT = os.getenv("USERS_HOST_PORT")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "27017"))
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


@pytest.fixture(scope="module")
async def token(http_service: Any) -> str:
    """Create a valid token."""
    url = f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/login"
    headers = {"content-type": "application/json"}
    request_body = {
        "username": os.getenv("ADMIN_USERNAME"),
        "password": os.getenv("ADMIN_PASSWORD"),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=request_body)
    if response.status_code != 200:
        logging.error(f"Got unexpected status {response.status_code} from {http_service}.")
    return response.json()["token"]


@pytest.fixture(scope="module", autouse=True)
async def clear_db() -> AsyncGenerator:
    """Delete all events before we start."""
    mongo = motor.motor_asyncio.AsyncIOMotorClient(
        host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASSWORD
    )
    try:
        await db_utils.drop_db_and_recreate_indexes(mongo, DB_NAME)
    except Exception as error:
        logging.exception(f"Failed to drop database {DB_NAME}: {error}")
        raise error

    yield

    try:
        await db_utils.drop_db(mongo, DB_NAME)
    except Exception as error:
        logging.exception(f"Failed to drop database {DB_NAME}: {error}")
        raise error


@pytest.fixture(scope="module")
async def photo() -> dict:
    """Photo object for testing."""
    return {
        "name": "IMG_6291.JPG",
        "is_photo_finish": False,
        "is_start_registration": False,
        "confidence": 0,
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "creation_time": "2022-03-05T06:41:52",
        "information": {"description": "Test photo for sprint"},
        "race_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "raceclass": "K-Jr",
        "biblist": [2, 4],
        "clublist": ["Kjelsås", "Lyn"],
        "g_id": "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK",
        "g_product_url": "https://photos.google.com/G4C9GZK",
        "g_base_url": "https://lh3.googleusercontent.com/f_AEeh",
        "ai_information": {"persons": "3", "numbers": [5], "texts": ["LYN"]},
    }


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_photo(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    photo: dict,
) -> None:
    """Should return Created, location header and no body."""
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    url = f"{http_service}/photos"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=photo)

    assert response.status_code == HTTPStatus.CREATED
    assert "/photos/" in response.headers["location"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_photos(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of photos as json."""
    url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["content-type"]
    photos = response.json()
    assert type(photos) is list
    assert len(photos) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_photo_by_id(
    http_service: Any, token: MockFixture, photo: dict
) -> None:
    """Should return OK and a photo as json."""
    list_url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        photos = response.json()
        p_id = photos[0]["id"]
        response = await client.get(f"{http_service}/photos/{p_id}")
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["content-type"]
    assert body["id"] == p_id
    assert body["name"] == photo["name"]
    assert body["creation_time"] == photo["creation_time"]
    assert body["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_photo(http_service: Any, token: MockFixture, photo: dict) -> None:
    """Should return No Content."""
    list_url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        photos = response.json()
        p_id = photos[0]["id"]
        photo_url = f"{http_service}/photos/{p_id}"

        request_body = deepcopy(photo)
        request_body["id"] = p_id
        request_body["name"] = "Oslo Skagen sprint updated"

        response = await client.put(photo_url, headers=headers, json=request_body)
        assert response.status_code == HTTPStatus.NO_CONTENT

        response = await client.get(photo_url)
        assert response.status_code == HTTPStatus.OK
        updated_photo = response.json()
        assert updated_photo["name"] == "Oslo Skagen sprint updated"
        assert updated_photo["creation_time"] == photo["creation_time"]
        assert updated_photo["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_photo(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    list_url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {"authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        photos = response.json()
        p_id = photos[0]["id"]
        photo_url = f"{http_service}/photos/{p_id}"
        response = await client.delete(photo_url, headers=headers)
        assert response.status_code == HTTPStatus.NO_CONTENT

        response = await client.get(photo_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
