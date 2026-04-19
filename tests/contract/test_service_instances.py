"""Contract test cases for service instances."""

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
        "action": "start",
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
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    url = f"{http_service}/service-instances"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=service_instance)

    assert response.status_code == HTTPStatus.CREATED
    assert "/service-instances/" in response.headers["location"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_service_instances(http_service: Any, token: MockFixture) -> None:
    """Should return OK and a list of service instances as json."""
    url = f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["content-type"]
    service_instances = response.json()
    assert type(service_instances) is list
    assert len(service_instances) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_service_instance_by_id(
    http_service: Any, token: MockFixture, service_instance: dict
) -> None:
    """Should return OK and a service instance as json."""
    list_url = f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        service_instances = response.json()
        si_id = service_instances[0]["id"]
        response = await client.get(f"{http_service}/service-instances/{si_id}")
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["content-type"]
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
    list_url = f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        service_instances = response.json()
        si_id = service_instances[0]["id"]
        si_url = f"{http_service}/service-instances/{si_id}"

        request_body = deepcopy(service_instance)
        request_body["id"] = si_id
        request_body["status"] = "error"

        response = await client.put(si_url, headers=headers, json=request_body)
        assert response.status_code == HTTPStatus.NO_CONTENT

        response = await client.get(si_url)
        assert response.status_code == HTTPStatus.OK
        updated = response.json()
        assert updated["status"] == "error"
        assert updated["service_type"] == service_instance["service_type"]
        assert updated["instance_name"] == service_instance["instance_name"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_service_instance(http_service: Any, token: MockFixture) -> None:
    """Should return No Content."""
    list_url = f"{http_service}/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758"
    headers = {"authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(list_url)
        service_instances = response.json()
        si_id = service_instances[0]["id"]
        si_url = f"{http_service}/service-instances/{si_id}"
        response = await client.delete(si_url, headers=headers)
        assert response.status_code == HTTPStatus.NO_CONTENT

        response = await client.get(si_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
