"""Contract test cases for config."""

import logging
import os
from collections.abc import AsyncGenerator
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


@pytest.fixture(scope="module", autouse=True)
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
        logging.error(
            f"Got unexpected status {response.status_code} from {http_service}."
        )
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
async def config() -> dict:
    """Test config object."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "photo_location",
        "value": "2024 Ragde-sprinten",
    }


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_config(
    http_service: Any,
    token: MockFixture,
    config: dict,
) -> None:
    """Should return Created, location header and no body."""
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    url = f"{http_service}/config"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=config)

    assert response.status_code == HTTPStatus.CREATED
    assert "/config/" in response.headers["location"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_config_by_key(
    http_service: Any, token: MockFixture, config: dict
) -> None:
    """Should return OK and a config as json."""
    url = f"{http_service}/config?eventId=1e95458c-e000-4d8b-beda-f860c77fd758&key=photo_location"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["content-type"]
    ret_config = response.json()
    assert type(ret_config) is dict
    assert ret_config["value"] == config["value"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_config_by_key_not_found(
    http_service: Any, token: MockFixture, config: dict
) -> None:
    """Should return 404 when key not found."""
    url = f"{http_service}/config?eventId=1e95458c-e000-4d8b-beda-f860c77fd758&key=invalid_key"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "application/json" in response.headers["content-type"]
