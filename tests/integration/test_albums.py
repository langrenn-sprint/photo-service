"""Integration test cases for the albums route."""

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
def album() -> dict:
    """Album object for testing."""
    return {
        "camera_position": "right",
        "changelog": [],
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "g_id": "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK",
        "is_photo_finish": True,
        "is_start_registration": False,
        "last_sync_time": "2022-09-25T16:41:52",
        "place": "finish",
        "sync_on": False,
        "title": "2022 Ragde-sprinten",
        "cover_photo_url": "",
    }


@pytest.mark.integration
def test_create_album(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    album: dict,
) -> None:
    """Should return Created, location header."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=test_a_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/albums", headers=headers, json=album)
    assert resp.status_code == HTTPStatus.CREATED
    assert f"/albums/{test_a_id}" in resp.headers["location"]


@pytest.mark.integration
def test_get_album_by_g_id(
    client: TestClient, mocker: MockFixture, token: str, album: dict
) -> None:
    """Should return OK, and a body containing one album."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    g_id = (
        "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK"
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_g_id",
        return_value={"id": test_a_id} | album,
    )

    resp = client.get(f"/albums?gId={g_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(album) is dict
    assert body["g_id"] == g_id
    assert body["place"] == album["place"]
    assert body["last_sync_time"] == album["last_sync_time"]


@pytest.mark.integration
def test_get_album_by_id(
    client: TestClient, mocker: MockFixture, token: str, album: dict
) -> None:
    """Should return OK, and a body containing one album."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id} | album,
    )

    resp = client.get(f"/albums/{test_a_id}")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    body = resp.json()
    assert type(album) is dict
    assert body["id"] == test_a_id
    assert body["place"] == album["place"]
    assert body["last_sync_time"] == album["last_sync_time"]


@pytest.mark.integration
def test_update_album_by_id(
    client: TestClient,
    mocker: MockFixture,
    token: str,
    album: dict,
) -> None:
    """Should return No Content."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id} | album,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value={"id": test_a_id} | album,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    new_name = "Oslo Skagen sprint Oppdatert"
    request_body = deepcopy(album)
    request_body["id"] = test_a_id
    request_body["place"] = new_name

    resp = client.put(f"/albums/{test_a_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.integration
def test_get_all_albums(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return OK and a valid json body."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_all_albums",
        return_value=[
            {
                "g_id": "google_album_id",
                "id": test_a_id,
                "place": "Oslo Skagen Sprint",
                "finish_line": False,
            }
        ],
    )

    resp = client.get("/albums")
    assert resp.status_code == HTTPStatus.OK
    assert "application/json" in resp.headers["content-type"]
    albums = resp.json()
    assert type(albums) is list
    assert len(albums) > 0
    assert albums[0]["id"] == test_a_id


@pytest.mark.integration
def test_delete_album_by_id(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return No Content."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=test_a_id,
    )
    headers = {
        "authorization": f"Bearer {token}",
    }

    resp = client.delete(f"/albums/{test_a_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NO_CONTENT


# Bad cases


@pytest.mark.integration
def test_create_album_missing_mandatory_property(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=test_a_id,
    )
    request_body = {"optional_property": "Optional_property"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/albums", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_album_with_input_id(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=test_a_id,
    )
    request_body = {"id": test_a_id, "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/albums", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_album_adapter_fails(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 400 HTTPBadRequest."""
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=None,
    )
    request_body = {"g_id": "google_album_id", "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    resp = client.post("/albums", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.integration
def test_update_album_by_id_missing_mandatory_property(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=test_a_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {"id": test_a_id, "optional_property": "Optional_property"}

    resp = client.put(f"/albums/{test_a_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_update_album_by_id_different_id_in_body(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=test_a_id,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {"id": "different_id", "place": "Oslo Skagen sprint Oppdatert"}

    resp = client.put(f"/albums/{test_a_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# Unauthorized cases:


@pytest.mark.integration
def test_create_album_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=test_a_id,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = {"content-type": "application/json"}

    resp = client.post("/albums", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_update_album_by_id_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": test_a_id, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=test_a_id,
    )

    headers = {"content-type": "application/json"}
    request_body = {"id": test_a_id, "place": "Oslo Skagen sprint Oppdatert"}

    resp = client.put(f"/albums/{test_a_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_delete_album_by_id_no_authorization(
    client: TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=test_a_id,
    )

    resp = client.delete(f"/albums/{test_a_id}")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


# Forbidden:
@pytest.mark.integration
def test_create_album_insufficient_role(
    client: TestClient, mocker: MockFixture, token_unsufficient_role: str
) -> None:
    """Should return 403 Forbidden."""
    test_a_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "app.services.albums_service.create_id",
        return_value=test_a_id,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=test_a_id,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token_unsufficient_role}",
    }

    resp = client.post("/albums", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.FORBIDDEN


# NOT FOUND CASES:


@pytest.mark.integration
def test_get_album_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    test_a_id = "does-not-exist"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )

    resp = client.get(f"/albums/{test_a_id}")
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_update_album_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    test_a_id = "does-not-exist"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=None,
    )

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    request_body = {
        "id": test_a_id,
        "g_id": "google_album_id",
        "place": "Oslo Skagen sprint Oppdatert",
    }

    resp = client.put(f"/albums/{test_a_id}", headers=headers, json=request_body)
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_delete_album_not_found(
    client: TestClient, mocker: MockFixture, token: str
) -> None:
    """Should return 404 Not found."""
    test_a_id = "does-not-exist"
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )
    mocker.patch(
        "app.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=None,
    )

    headers = {
        "authorization": f"Bearer {token}",
    }
    resp = client.delete(f"/albums/{test_a_id}", headers=headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND
