"""Integration test cases for the config route."""

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
    """Create a valid token."""
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
async def config() -> dict:
    """Config object for testing."""
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
    """Test Return Created, location header."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.config_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value={},
    )

    request_body = config

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.CREATED
        assert f"/config/{test_a_id}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_config_by_key(
    client: _TestClient, mocker: MockFixture, token: MockFixture, config: dict
) -> None:
    """Test return OK, and a body containing one config."""
    key = "video_config"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    value = "2024 Ragde-sprinten"

    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=config,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/config?count=25&eventId={event_id}&key={key}")
        assert resp.status == HTTPStatus.OK
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
        return_value=list_config,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get("/configs")
        assert resp.status == HTTPStatus.OK
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
        return_value=list_config,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/configs?&eventId={event_id}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(body) is list
        assert body[0]["value"] == value


# Bad cases
@pytest.mark.integration
async def test_create_config_key_exists(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    config: dict,
) -> None:
    """Should return Created, location header."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.config_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=config,
    )

    request_body = config

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


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
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
async def test_delete_config_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    test_a_id = "dummy"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.delete_config",
        return_value=test_a_id,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.delete(f"/config/{test_a_id}", headers=headers)
        assert resp.status == HTTPStatus.NOT_FOUND


# Unauthorized cases:


@pytest.mark.integration
async def test_create_config_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=401)

        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNAUTHORIZED


# Forbidden:
@pytest.mark.integration
async def test_create_config_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=403)
        resp = await client.post("/config", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.FORBIDDEN
