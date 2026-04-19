"""Integration test cases for the status route."""

import os
from http import HTTPStatus

import jwt
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Token."""
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
def status() -> dict:
    """Status object for testing."""
    return {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "time": "2022-09-25T16:41:52",
        "type": "video_status",
        "message": "2022 Ragde-sprinten",
        "details": {"info1": "detail1", "info2": "detail2"},
    }


@pytest.mark.integration
def test_create_status(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    status: dict,
) -> None:
    """Test create status."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.status_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.create_status",
        return_value=test_a_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/status", headers=headers, json=status)
    assert resp.status_code == HTTPStatus.CREATED
    assert f"/status/{test_a_id}" in resp.headers["location"]


@pytest.mark.integration
def test_get_all_status(
    client: TestClient, mocker: MockFixture, token: str, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = [status]
    event_id = status["event_id"]

    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.get_all_status",
        return_value=status_list,
    )

    resp = client.get(f"/status?count=25&eventId={event_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is list
    assert body[0]["time"] == status["time"]


@pytest.mark.integration
def test_get_all_status_by_type(
    client: TestClient, mocker: MockFixture, token: str, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = [status]
    status_type = "video_status"
    event_id = status["event_id"]

    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.get_all_status_by_type",
        return_value=status_list,
    )

    resp = client.get(f"/status?count=25&eventId={event_id}&type={status_type}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is list
    assert body[0]["time"] == status["time"]


@pytest.mark.integration
def test_get_all_status_no_limit(
    client: TestClient, mocker: MockFixture, token: str, status: dict
) -> None:
    """Should return OK, and a body containing one status."""
    status_list = [status]
    event_id = status["event_id"]

    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.get_all_status",
        return_value=status_list,
    )

    resp = client.get(f"/status?eventId={event_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(body) is list
    assert body[0]["time"] == status["time"]


# Bad cases


@pytest.mark.integration
def test_create_status_adapter_fails(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422."""
    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.create_status",
        return_value=None,
    )
    request_body = {"g_id": "google_status_id", "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/status", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_delete_status_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not Found."""
    test_a_id = "dummy"
    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.get_status_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.delete_status",
        return_value=test_a_id,
    )
    headers = {
        "authorization": f"Bearer {token}",
    }

    resp = client.delete(f"/status/{test_a_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND


# Forbidden:
@pytest.mark.integration
def test_create_status_insufficient_role(
    client: TestClient, mocker: MockFixture, token_unsufficient_role: str
) -> None:
    """Should return 403 Forbidden."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.status_adapter.StatusAdapter.create_status",
        return_value=test_a_id,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token_unsufficient_role}",
    }

    resp = client.post("/status", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.FORBIDDEN
