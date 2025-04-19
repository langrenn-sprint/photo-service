"""Contract test cases for ping."""

import logging
import os
from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Any

import jwt
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


@pytest.fixture(scope="module", autouse=True)
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
async def config() -> dict:
    """Test config object."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "photo_location",
        "value": "2024 Ragde-sprinten",
    }


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unit_test_create_config(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        url = f"{http_service}/unit_test?domain=config&action=1"
        request_body = ""

        async with session.get(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == HTTPStatus.CREATED


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_config_by_key(
    http_service: Any, token: MockFixture, config: dict
) -> None:
    """Should return OK and an photo as json."""
    url = f"{http_service}/config?eventId=1e95458c-e000-4d8b-beda-f860c77fd758&key=photo_location"

    async with ClientSession() as session:
        async with session.get(url) as response:
            ret_config = await response.json()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(ret_config) is dict
    assert ret_config["value"] == config["value"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_config_by_key_not_found(
    http_service: Any, token: MockFixture, config: dict
) -> None:
    """Should return OK and an photo as json."""
    url = f"{http_service}/config?eventId=1e95458c-e000-4d8b-beda-f860c77fd758&key=invalid_key"

    async with ClientSession() as session:
        async with session.get(url) as response:
            ret_config = await response.json()

    assert response.status == HTTPStatus.NOT_FOUND
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
