"""Integration test cases for the service instances route."""

import os
from copy import deepcopy
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
    payload = {
        "username": os.getenv("ADMIN_USERNAME"),
        "role": "admin",
        "exp": 9999999999,
    }
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def token_insufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"username": "user", "role": "user", "exp": 9999999999}
    return jwt.encode(payload, secret, algorithm)


@pytest.fixture
def service_instance() -> dict:
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


@pytest.mark.integration
def test_create_service_instance(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    service_instance: dict,
) -> None:
    """Should return Created, location header."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=si_id,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=si_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/service-instances", headers=headers, json=service_instance)
    assert resp.status_code == HTTPStatus.CREATED
    assert f"/service-instances/{si_id}" in resp.headers["location"]


@pytest.mark.integration
def test_get_service_instance_by_id(
    client: TestClient, mocker: MockFixture, token: str, service_instance: dict
) -> None:
    """Should return OK, and a body containing one service instance."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={"id": si_id} | service_instance,
    )

    resp = client.get(f"/service-instances/{si_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(service_instance) is dict
    assert body["id"] == si_id
    assert body["service_type"] == service_instance["service_type"]
    assert body["instance_name"] == service_instance["instance_name"]
    assert body["status"] == service_instance["status"]


@pytest.mark.integration
def test_update_service_instance_by_id(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    service_instance: dict,
) -> None:
    """Should return No Content."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={"id": si_id} | service_instance,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.update_service_instance",
        return_value={"id": si_id} | service_instance,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    new_status = "error"
    request_body = deepcopy(service_instance)
    request_body["id"] = si_id
    request_body["status"] = new_status

    resp = client.put(f"/service-instances/{si_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.integration
def test_get_all_service_instances(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return OK and a valid json body."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_all_service_instances",
        return_value=[
            {
                "id": si_id,
                "service_type": "video-service",
                "instance_name": "video-service-1",
                "status": "running",
                "host_name": "localhost",
                "action": "start",
            }
        ],
    )

    resp = client.get("/service-instances?eventId=1e95458c-e000-4d8b-beda-f860c77fd758")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    service_instances = resp.json()
    assert type(service_instances) is list
    assert len(service_instances) > 0
    assert si_id == service_instances[0]["id"]


@pytest.mark.integration
def test_get_service_instances_by_service_type(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return OK and a valid json body."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    service_type = "video-service"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instances_by_service_type",
        return_value=[
            {
                "id": si_id,
                "service_type": service_type,
                "instance_name": "video-service-1",
                "status": "running",
                "host_name": "localhost",
                "action": "start",
            }
        ],
    )

    resp = client.get(
        f"/service-instances?eventId={event_id}&serviceType={service_type}"
    )
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    service_instances = resp.json()
    assert type(service_instances) is list
    assert len(service_instances) > 0
    assert service_type == service_instances[0]["service_type"]


@pytest.mark.integration
def test_get_service_instances_by_status(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return OK and a valid json body."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    status = "running"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instances_by_status",
        return_value=[
            {
                "id": si_id,
                "service_type": "video-service",
                "instance_name": "video-service-1",
                "status": status,
                "host_name": "localhost",
                "action": "start",
            }
        ],
    )

    resp = client.get(f"/service-instances?eventId={event_id}&status={status}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    service_instances = resp.json()
    assert type(service_instances) is list
    assert len(service_instances) > 0
    assert status == service_instances[0]["status"]


@pytest.mark.integration
def test_delete_service_instance_by_id(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return No Content."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={
            "id": si_id,
            "service_type": "video-service",
            "instance_name": "video-service-1",
            "status": "running",
            "host_name": "localhost",
            "action": "start",
        },
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.delete_service_instance",
        return_value=si_id,
    )
    headers = {
        "authorization": f"Bearer {token}",
    }

    resp = client.delete(f"/service-instances/{si_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NO_CONTENT


# Bad cases


@pytest.mark.integration
def test_create_service_instance_missing_mandatory_property(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=si_id,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=si_id,
    )
    request_body = {"optional_property": "Optional_property"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/service-instances", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_service_instance_with_input_id(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=si_id,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=si_id,
    )
    request_body = {
        "id": si_id,
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/service-instances", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_service_instance_adapter_fails(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 400 HTTPBadRequest."""
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=None,
    )
    request_body = {
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/service-instances", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.integration
def test_update_service_instance_by_id_missing_mandatory_property(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={
            "id": si_id,
            "service_type": "video-service",
            "instance_name": "video-service-1",
            "status": "running",
            "host_name": "localhost",
            "action": "start",
        },
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.update_service_instance",
        return_value=si_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {"id": si_id, "optional_property": "Optional_property"}

    resp = client.put(f"/service-instances/{si_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_update_service_instance_by_id_different_id_in_body(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={
            "id": si_id,
            "service_type": "video-service",
            "instance_name": "video-service-1",
            "status": "running",
            "host_name": "localhost",
            "action": "start",
        },
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.update_service_instance",
        return_value=si_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {
        "id": "different_id",
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }

    resp = client.put(f"/service-instances/{si_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# Unauthorized cases:


@pytest.mark.integration
def test_create_service_instance_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=si_id,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=si_id,
    )

    request_body = {
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }
    headers = {"content-type": "application/json"}

    resp = client.post("/service-instances", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_update_service_instance_by_id_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value={
            "id": si_id,
            "service_type": "video-service",
            "instance_name": "video-service-1",
            "status": "running",
            "host_name": "localhost",
            "action": "start",
        },
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.update_service_instance",
        return_value=si_id,
    )

    headers = {"content-type": "application/json"}
    request_body = {
        "id": si_id,
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }

    resp = client.put(f"/service-instances/{si_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_delete_service_instance_by_id_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.delete_service_instance",
        return_value=si_id,
    )

    resp = client.delete(f"/service-instances/{si_id}")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


# Forbidden:
@pytest.mark.integration
def test_create_service_instance_insufficient_role(
    client: TestClient, mocker: MockFixture, token_insufficient_role: str
) -> None:
    """Should return 403 Forbidden."""
    si_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.service_instances_service.create_id",
        return_value=si_id,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.create_service_instance",
        return_value=si_id,
    )
    request_body = {
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token_insufficient_role}",
    }

    resp = client.post("/service-instances", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.FORBIDDEN


# NOT FOUND CASES:


@pytest.mark.integration
def test_get_service_instance_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    si_id = "does-not-exist"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value=None,
    )

    resp = client.get(f"/service-instances/{si_id}")
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_update_service_instance_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    si_id = "does-not-exist"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.update_service_instance",
        return_value=None,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {
        "id": "290e70d5-0933-4af0-bb53-1d705ba7eb95",
        "service_type": "video-service",
        "instance_name": "video-service-1",
        "status": "running",
        "host_name": "localhost",
        "action": "start",
    }

    resp = client.put(f"/service-instances/{si_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_delete_service_instance_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    si_id = "does-not-exist"
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.get_service_instance_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.service_instances_adapter.ServiceInstancesAdapter.delete_service_instance",
        return_value=None,
    )

    headers = {
        "authorization": f"Bearer {token}",
    }
    resp = client.delete(f"/service-instances/{si_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND
