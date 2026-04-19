"""Integration test cases for the config route."""

import os
from http import HTTPStatus

import jwt
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"username": os.getenv("ADMIN_USERNAME"), "role": "admin", "exp": 9999999999}
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def token_unsufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"username": "user", "role": "user", "exp": 9999999999}
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def config() -> dict:
    """Config object for testing."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "video_config",
        "value": "2024 Ragde-sprinten",
    }


@pytest.mark.integration
def test_create_config(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    config: dict,
) -> None:
    """Test Return Created, location header."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.config_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=None,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/config", headers=headers, json=config)
    assert resp.status_code == HTTPStatus.CREATED
    assert f"/config/{test_a_id}" in resp.headers["location"]


@pytest.mark.integration
def test_get_config_by_key(
    client: TestClient, mocker: MockFixture, token: str, config: dict
) -> None:
    """Test return OK, and a body containing one config."""
    key = "video_config"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    value = "2024 Ragde-sprinten"

    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=config,
    )

    resp = client.get(f"/config?count=25&eventId={event_id}&key={key}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is dict
    assert body["value"] == value


@pytest.mark.integration
def test_get_all_configs(
    client: TestClient, mocker: MockFixture, token: str, config: dict
) -> None:
    """Should return OK, and a body containing list with one config."""
    value = "2024 Ragde-sprinten"
    list_config = [config]

    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_all_configs",
        return_value=list_config,
    )

    resp = client.get("/configs")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is list
    assert body[0]["value"] == value


@pytest.mark.integration
def test_get_all_configs_by_event(
    client: TestClient, mocker: MockFixture, token: str, config: dict
) -> None:
    """Should return OK, and a body containing list with one config."""
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    value = "2024 Ragde-sprinten"
    list_config = [config]

    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_all_configs_by_event",
        return_value=list_config,
    )

    resp = client.get(f"/configs?&eventId={event_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is list
    assert body[0]["value"] == value


# Bad cases
@pytest.mark.integration
def test_create_config_key_exists(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    config: dict,
) -> None:
    """Should return 422 when key already exists."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.config_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_config_by_key",
        return_value=config,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/config", headers=headers, json=config)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_config_adapter_fails(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422."""
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=None,
    )
    request_body = {"g_id": "google_config_id"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/config", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_delete_config_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not Found."""
    test_a_id = "dummy"
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.get_config_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.delete_config",
        return_value=test_a_id,
    )
    headers = {
        "authorization": f"Bearer {token}",
    }

    resp = client.delete(f"/config/{test_a_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND


# Unauthorized cases:


@pytest.mark.integration
def test_create_config_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = {"content-type": "application/json"}

    resp = client.post("/config", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


# Forbidden:
@pytest.mark.integration
def test_create_config_insufficient_role(
    client: TestClient, mocker: MockFixture, token_unsufficient_role: str
) -> None:
    """Should return 403 Forbidden."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.config_adapter.ConfigAdapter.create_config",
        return_value=test_a_id,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token_unsufficient_role}",
    }

    resp = client.post("/config", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.FORBIDDEN
