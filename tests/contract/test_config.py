"""Contract test cases for ping."""
import logging
import os
from typing import Any, AsyncGenerator

from aiohttp import ClientSession, hdrs
import motor.motor_asyncio
import pytest
from pytest_mock import MockFixture

from photo_service.utils import db_utils

USERS_HOST_SERVER = os.getenv("USERS_HOST_SERVER")
USERS_HOST_PORT = os.getenv("USERS_HOST_PORT")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 27017))
DB_NAME = os.getenv("DB_NAME", "events_test")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


@pytest.fixture(scope="module")
@pytest.mark.asyncio(scope="module")
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


@pytest.fixture(scope="module", autouse=True)
@pytest.mark.asyncio(scope="module")
async def clear_db() -> AsyncGenerator:
    """Delete all events before we start."""
    mongo = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore
        host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASSWORD
    )
    try:
        await db_utils.drop_db_and_recreate_indexes(mongo, DB_NAME)
    except Exception as error:
        logging.error(f"Failed to drop database {DB_NAME}: {error}")
        raise error

    yield

    try:
        await db_utils.drop_db(mongo, DB_NAME)
    except Exception as error:
        logging.error(f"Failed to drop database {DB_NAME}: {error}")
        raise error


@pytest.fixture(scope="module")
async def config() -> dict:
    """A config object for testing."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "video_config",
        "value": "2024 Ragde-sprinten",
    }


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_create_config(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    config: dict,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        url = f"{http_service}/config"
        request_body = config

        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == 201
        assert "/config/" in response.headers[hdrs.LOCATION]


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_all_configs(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of configs as json."""
    url = f"{http_service}/configs"

    session = ClientSession()
    async with session.get(url) as response:
        configs = await response.json()
    await session.close()

    assert response.status == 200
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(configs) is list
    assert len(configs) > 0


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_get_config_by_key(
    http_service: Any, token: MockFixture, config: dict
) -> None:
    """Should return OK and an config as json."""
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    key = "video_config"
    value = "2024 Ragde-sprinten"
    url = f"{http_service}/config"
    url = f"{url}?key={key}&event_id={event_id}"

    async with ClientSession() as session:
        async with session.get(url) as response:
            body = await response.json()

    assert response.status == 200
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(config) is dict
    assert body["value"] == value
