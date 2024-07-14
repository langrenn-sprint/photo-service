"""Integration test cases for the status route."""
import os

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
import jwt
from multidict import MultiDict
import pytest
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": os.getenv("ADMIN_USERNAME"), "roles": ["admin"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
def token_unsufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": "user", "roles": ["user"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
async def status() -> dict:
    """An status object for testing."""
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
    """Should return Created, location header."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.status_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=ID,
    )

    request_body = status

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == 201
        assert f"/status/{ID}" in resp.headers[hdrs.LOCATION]


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
        return_value=status_list,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/status?count=25&eventId={event_id}")
        assert resp.status == 200
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
        return_value=status_list,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(
            f"/status?count=25&eventId={event_id}&type={status_type}"
        )
        assert resp.status == 200
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
        return_value=status_list,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/status?eventId={event_id}")
        assert resp.status == 200
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
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_delete_status_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    ID = "dummy"
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.delete_status",
        return_value=ID,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.delete(f"/status/{ID}", headers=headers)
        assert resp.status == 404


# Unauthorized cases:


@pytest.mark.integration
async def test_create_status_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=ID,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == 401


# Forbidden:
@pytest.mark.integration
async def test_create_status_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.status_adapter.StatusAdapter.create_status",
        return_value=ID,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=403)
        resp = await client.post("/status", headers=headers, json=request_body)
        assert resp.status == 403
