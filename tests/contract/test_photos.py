"""Contract test cases for ping."""

import logging
import os
from collections.abc import AsyncGenerator
from copy import deepcopy
from http import HTTPStatus
from typing import Any

import motor.motor_asyncio
import pytest
from aiohttp import ClientSession, hdrs
from pytest_mock import MockFixture

from photo_service.utils import db_utils

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
    headers = {hdrs.CONTENT_TYPE: "application/json"}
    request_body = {
        "username": os.getenv("ADMIN_USERNAME"),
        "password": os.getenv("ADMIN_PASSWORD"),
    }
    session = ClientSession()
    async with session.post(url, headers=headers, json=request_body) as response:
        body = await response.json()
    await session.close()
    if response.status != HTTPStatus.OK:
        logging.error(f"Got unexpected status {response.status} from {http_service}.")
    return body["token"]


@pytest.fixture(scope="module", autouse=True)
async def clear_db() -> AsyncGenerator:
    """Delete all events before we start."""
    mongo = motor.motor_asyncio.AsyncIOMotorClient(
        host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASSWORD
    )
    try:
        await db_utils.drop_db_and_recreate_indexes(mongo, DB_NAME)
    except Exception:
        logging.exception(f"Failed to drop database {DB_NAME}")
        raise

    yield

    try:
        await db_utils.drop_db(mongo, DB_NAME)
    except Exception:
        logging.exception(f"Failed to drop database {DB_NAME}")
        raise


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
        "information": "Test photo for sprint",
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
@pytest.mark.asyncio(scope="module")
async def test_create_photo(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    photo: dict,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        url = f"{http_service}/photos"
        request_body = photo

        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == HTTPStatus.CREATED
        assert "/photos/" in response.headers[hdrs.LOCATION]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_all_photos(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of photos as json."""
    url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"

    session = ClientSession()
    async with session.get(url) as response:
        photos = await response.json()
    await session.close()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(photos) is list
    assert len(photos) > 0


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_photo_by_id(
    http_service: Any, token: MockFixture, photo: dict
) -> None:
    """Should return OK and an photo as json."""
    url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        p_id = photos[0]["id"]
        url = f"{http_service}/photos/{p_id}"
        async with session.get(url) as response:
            body = await response.json()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(photo) is dict
    assert body["id"] == p_id
    assert body["name"] == photo["name"]
    assert body["creation_time"] == photo["creation_time"]
    assert body["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_update_photo(http_service: Any, token: MockFixture, photo: dict) -> None:
    """Should return No Content."""
    url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        p_id = photos[0]["id"]
        url = f"{http_service}/photos/{p_id}"

        request_body = deepcopy(photo)
        new_name = "Oslo Skagen sprint updated"
        request_body["id"] = p_id
        request_body["name"] = new_name

        async with session.put(url, headers=headers, json=request_body) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.OK
            updated_photo = await response.json()
            assert updated_photo["name"] == new_name
            assert updated_photo["creation_time"] == photo["creation_time"]
            assert updated_photo["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_delete_photo(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    url = f"{http_service}/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        p_id = photos[0]["id"]
        url = f"{http_service}/photos/{p_id}"
        async with session.delete(url, headers=headers) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.NOT_FOUND
