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
async def album() -> dict:
    """Album object for testing."""
    return {
        "camera_position": "right",
        "changelog": [],
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "g_id": "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK",
        "is_photo_finish": True,
        "is_start_registration": False,
        "last_sync_time": "2022-09-25T16:41:52",
        "place": "finish",
        "sync_on": False,
        "title": "2022 Ragde-sprinten",
        "cover_photo_url": "",
    }


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_create_album(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    album: dict,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        url = f"{http_service}/albums"
        request_body = album

        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == HTTPStatus.CREATED
        assert "/albums/" in response.headers[hdrs.LOCATION]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_all_albums(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of albums as json."""
    url = f"{http_service}/albums"

    session = ClientSession()
    async with session.get(url) as response:
        albums = await response.json()
    await session.close()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(albums) is list
    assert len(albums) > 0


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_album_by_id(
    http_service: Any, token: MockFixture, album: dict
) -> None:
    """Should return OK and an album as json."""
    url = f"{http_service}/albums"

    async with ClientSession() as session:
        async with session.get(url) as response:
            albums = await response.json()
        a_id = albums[0]["id"]
        url = f"{url}/{a_id}"
        async with session.get(url) as response:
            body = await response.json()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(album) is dict
    assert body["id"] == a_id
    assert body["last_sync_time"] == album["last_sync_time"]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_update_album(http_service: Any, token: MockFixture, album: dict) -> None:
    """Should return No Content."""
    url = f"{http_service}/albums"
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            albums = await response.json()
        a_id = albums[0]["id"]
        g_id = albums[0]["g_id"]
        url = f"{url}/{a_id}"

        request_body = deepcopy(album)
        new_name = "Oslo Skagen sprint updated"
        request_body["id"] = a_id
        request_body["g_id"] = g_id
        request_body["place"] = new_name

        async with session.put(url, headers=headers, json=request_body) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.OK
            updated_album = await response.json()
            assert updated_album["g_id"] == album["g_id"]
            assert updated_album["place"] == new_name


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_delete_album(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    url = f"{http_service}/albums"
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            albums = await response.json()
        a_id = albums[0]["id"]
        url = f"{url}/{a_id}"
        async with session.delete(url, headers=headers) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.NOT_FOUND
