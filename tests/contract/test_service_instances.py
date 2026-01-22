"""Contract test cases for service instances."""

import logging
import os
from collections.abc import AsyncGenerator
from copy import deepcopy
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
    if response.status != 200:
        logging.error(f"Got unexpected status {response.status} from {http_service}.")
    return body["token"]


@pytest.fixture(scope="module", autouse=True)
async def clear_db() -> AsyncGenerator:
    """Delete all service instances before we start."""
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
async def service_instance() -> dict:
    """Service instance object for testing."""
    return {
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "port": 8081,
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "started_at": "2024-03-05T06:41:52",
        "last_heartbeat": "2024-03-05T06:45:52",
        "metadata": {"version": "1.0.0"},
    }


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_service_instance(
    http_service: Any,
    token: MockFixture,
    clear_db: AsyncGenerator,
    service_instance: dict,
) -> None:
    """Should return Created, location header and no body."""
    async with ClientSession() as session:
        headers = {
            hdrs.CONTENT_TYPE: "application/json",
            hdrs.AUTHORIZATION: f"Bearer {token}",
        }
        url = f"{http_service}/service-instances"
        request_body = service_instance

        async with session.post(url, headers=headers, json=request_body) as response:
            status = response.status

        assert status == HTTPStatus.CREATED
        assert "/service-instances/" in response.headers[hdrs.LOCATION]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_service_instances(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of service instances as json."""
    url = (
        f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    )

    session = ClientSession()
    async with session.get(url) as response:
        service_instances = await response.json()
    await session.close()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(service_instances) is list
    assert len(service_instances) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_service_instance_by_id(
    http_service: Any, token: MockFixture, service_instance: dict
) -> None:
    """Should return OK and a service instance as json."""
    url = (
        f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    )

    async with ClientSession() as session:
        async with session.get(url) as response:
            service_instances = await response.json()
        si_id = service_instances[0]["id"]
        url = f"{http_service}/service-instances/{si_id}"
        async with session.get(url) as response:
            body = await response.json()

    assert response.status == HTTPStatus.OK
    assert "application/json" in response.headers[hdrs.CONTENT_TYPE]
    assert type(service_instance) is dict
    assert body["id"] == si_id
    assert body["service_type"] == service_instance["service_type"]
    assert body["instance_name"] == service_instance["instance_name"]
    assert body["status"] == service_instance["status"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_service_instance(
    http_service: Any, token: MockFixture, service_instance: dict
) -> None:
    """Should return No Content."""
    url = (
        f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    )
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            service_instances = await response.json()
        si_id = service_instances[0]["id"]
        url = f"{http_service}/service-instances/{si_id}"

        request_body = deepcopy(service_instance)
        new_status = "error"
        request_body["id"] = si_id
        request_body["status"] = new_status

        async with session.put(url, headers=headers, json=request_body) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.OK
            updated_service_instance = await response.json()
            assert updated_service_instance["status"] == new_status
            assert (
                updated_service_instance["service_type"]
                == service_instance["service_type"]
            )
            assert (
                updated_service_instance["instance_name"]
                == service_instance["instance_name"]
            )


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_service_instance(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    url = (
        f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    async with ClientSession() as session:
        async with session.get(url) as response:
            service_instances = await response.json()
        si_id = service_instances[0]["id"]
        url = f"{http_service}/service-instances/{si_id}"
        async with session.delete(url, headers=headers) as response:
            assert response.status == HTTPStatus.NO_CONTENT

        async with session.get(url) as response:
            assert response.status == HTTPStatus.NOT_FOUND
