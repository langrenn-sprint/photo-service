"""Contract test cases for ping."""
import asyncio
from copy import deepcopy
from json import load
import logging
import os
from typing import Any, AsyncGenerator

from aiohttp import ClientSession, hdrs
import pytest
from pytest_mock import MockFixture

USERS_HOST_SERVER = os.getenv("USERS_HOST_SERVER")
USERS_HOST_PORT = os.getenv("USERS_HOST_PORT")


@pytest.fixture(scope="module")
def event_loop(request: Any) -> Any:
    """Redefine the event_loop fixture to have the same scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
@pytest.mark.asyncio
async def clear_db(http_service: Any, token: MockFixture) -> AsyncGenerator:
    """Delete all photos before we start."""
    url = f"{http_service}/photos"
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    session = ClientSession()
    async with session.get(url) as response:
        photos = await response.json()
        for photo in photos:
            photo_id = photo["id"]
            async with session.delete(f"{url}/{photo_id}", headers=headers) as response:
                pass
    await session.close()
    yield


@pytest.fixture(scope="module")
async def photo() -> dict:
    """An photo object for testing."""
    return {
        "name": "Oslo Skagen sprint",
        "competition_format": "Interval Start",
        "date_of_photo": "2021-08-31",
        "time_of_photo": "09:00:00",
        "organiser": "Lyn Ski",
        "webpage": "https://example.com",
        "information": "Testarr for å teste den nye løysinga.",
    }


@pytest.fixture(scope="module")
@pytest.mark.asyncio
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
    if response.status != 200:
        logging.error(f"Got unexpected status {response.status} from {http_service}.")
    return body["token"]


@pytest.fixture(scope="module")
async def competition_format_interval_start() -> dict:
    """An competition_format object for testing."""
    with open("tests/files/competition_format.json", "r") as file:
        competition_format = load(file)
    return competition_format


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_photo(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    photo: dict,
    competition_format_interval_start: dict,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        # We have to create a competition_format:
        url = f"{http_service}/competition-formats"
        request_body = competition_format_interval_start
        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status
            assert status == 201

        url = f"{http_service}/photos"
        request_body = photo

        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == 201
        assert "/photos/" in response.headers[hdrs.LOCATION]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_photos(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of photos as json."""
    url = f"{http_service}/photos"

    session = ClientSession()
    async with session.get(url) as response:
        photos = await response.json()
    await session.close()

    assert response.status == 200
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(photos) is list
    assert len(photos) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_photo_by_id(
    http_service: Any, token: MockFixture, photo: dict
) -> None:
    """Should return OK and an photo as json."""
    url = f"{http_service}/photos"

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        id = photos[0]["id"]
        url = f"{url}/{id}"
        async with session.get(url) as response:
            body = await response.json()

    assert response.status == 200
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(photo) is dict
    assert body["id"] == id
    assert body["name"] == photo["name"]
    assert body["competition_format"] == photo["competition_format"]
    assert body["date_of_photo"] == photo["date_of_photo"]
    assert body["time_of_photo"] == photo["time_of_photo"]
    assert body["organiser"] == photo["organiser"]
    assert body["webpage"] == photo["webpage"]
    assert body["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_photo(http_service: Any, token: MockFixture, photo: dict) -> None:
    """Should return No Content."""
    url = f"{http_service}/photos"
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        id = photos[0]["id"]
        url = f"{url}/{id}"

        request_body = deepcopy(photo)
        new_name = "Oslo Skagen sprint updated"
        request_body["id"] = id
        request_body["name"] = new_name

        async with session.put(url, headers=headers, json=request_body) as response:
            assert response.status == 204

        async with session.get(url) as response:
            assert response.status == 200
            updated_photo = await response.json()
            assert updated_photo["name"] == new_name
            assert updated_photo["competition_format"] == photo["competition_format"]
            assert updated_photo["date_of_photo"] == photo["date_of_photo"]
            assert updated_photo["time_of_photo"] == photo["time_of_photo"]
            assert updated_photo["organiser"] == photo["organiser"]
            assert updated_photo["webpage"] == photo["webpage"]
            assert updated_photo["information"] == photo["information"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_photo(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    url = f"{http_service}/photos"
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            photos = await response.json()
        id = photos[0]["id"]
        url = f"{url}/{id}"
        async with session.delete(url, headers=headers) as response:
            assert response.status == 204

        async with session.get(url) as response:
            assert response.status == 404
