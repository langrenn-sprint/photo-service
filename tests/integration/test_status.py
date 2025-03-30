"""Integration test cases for the status route."""

import os
from http import HTTPStatus

import jwt
import pytest
from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
from dotenv import load_dotenv
from multidict import MultiDict
from pytest_mock import MockFixture

load_dotenv()

USERS_HOST_SERVER = os.getenv("USERS_HOST_SERVER", "localhost")
USERS_HOST_PORT = os.getenv("USERS_HOST_PORT", "8086")


@pytest.fixture
def token() -> str:
    """Token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": os.getenv("ADMIN_USERNAME"), "roles": ["admin"]}
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def token_unsufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": "user", "roles": ["user"]}
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
async def status() -> dict:
    """Status object for testing."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "time": "2022-09-25T16:41:52",
        "type": "video_status",
        "message": "2022 Ragde-sprinten",
    }


@pytest.mark.integration
async def test_create_status(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    status: dict,
) -> None:
    """Test create status."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.status_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=test_a_id,
    )

    request_body = status

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.CREATED
        assert f"/status/{test_a_id}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_all_status(
    client: _TestClient, mocker: MockFixture, token: MockFixture, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = []
    status_list.append(status)
    event_id = status["event_id"]

    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.get_all_status",
        return_value=status_list,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/status?count=25&eventId={event_id}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["time"] == status["time"]


@pytest.mark.integration
async def test_get_all_status_by_type(
    client: _TestClient, mocker: MockFixture, token: MockFixture, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = []
    status_list.append(status)
    status_type = "video_status"
    event_id = status["event_id"]

    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.get_all_status_by_type",
        return_value=status_list,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(
            f"/status?count=25&eventId={event_id}&type={status_type}"
        )
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["time"] == status["time"]


@pytest.mark.integration
async def test_get_all_status_no_limit(
    client: _TestClient, mocker: MockFixture, token: MockFixture, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = []
    status_list.append(status)
    event_id = status["event_id"]

    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.get_all_status",
        return_value=status_list,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/status?eventId={event_id}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["time"] == status["time"]


# Bad cases


# Mandatory properties missing at create and update:
@pytest.mark.integration
async def test_create_status_adapter_fails(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422."""
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=None,
    )
    request_body = {"g_id": "google_status_id", "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
async def test_delete_status_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    test_a_id = "dummy"
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.delete_status",
        return_value=test_a_id,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.delete(f"/status/{test_a_id}", headers=headers)
        assert resp.status == HTTPStatus.NOT_FOUND


# Forbidden:
@pytest.mark.integration
async def test_create_status_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=test_a_id,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=403)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.FORBIDDEN
