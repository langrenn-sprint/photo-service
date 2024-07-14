"""Integration test cases for the config route."""
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
async def config() -> dict:
    """An config object for testing."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "video_config",
        "value": "2024 Ragde-sprinten",
    }


@pytest.mark.integration
async def test_create_config(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    config: dict,
) -> None:
    """Should return Created, location header."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.config_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=ID,
    )

    request_body = config

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == 201
        assert f"/config/{ID}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_config_by_key(
    client: _TestClient, mocker: MockFixture, token: MockFixture, config: dict
) -> None:
    """Should return OK, and a body containing one config."""
    key = "video_config"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    value = "2024 Ragde-sprinten"

    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=config,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/config?count=25&eventId={event_id}&key={key}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is dict
        assert body["value"] == value


@pytest.mark.integration
async def test_get_all_configs(
    client: _TestClient, mocker: MockFixture, token: MockFixture, config: dict
) -> None:
    """Should return OK, and a body containing list with one config."""
    value = "2024 Ragde-sprinten"
    list_config = []
    list_config.append(config)

    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_all_configs",
        return_value=list_config,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get("/configs")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["value"] == value


@pytest.mark.integration
async def test_get_all_configs_by_event(
    client: _TestClient, mocker: MockFixture, token: MockFixture, config: dict
) -> None:
    """Should return OK, and a body containing list with one config."""
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    value = "2024 Ragde-sprinten"
    list_config = []
    list_config.append(config)

    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_all_configs_by_event",
        return_value=list_config,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/configs?&eventId={event_id}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["value"] == value


# Bad cases


# Mandatory properties missing at create and update:
@pytest.mark.integration
async def test_create_config_adapter_fails(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422."""
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=None,
    )
    request_body = {"g_id": "google_config_id"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_delete_config_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    ID = "dummy"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.delete_config",
        return_value=ID,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.delete(f"/config/{ID}", headers=headers)
        assert resp.status == 404


# Unauthorized cases:


@pytest.mark.integration
async def test_create_config_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=ID,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == 401


# Forbidden:
@pytest.mark.integration
async def test_create_config_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=ID,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=403)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == 403
