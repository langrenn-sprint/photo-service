"""Integration test cases for the albums route."""
from copy import deepcopy
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
async def album() -> dict:
    """An album object for testing."""
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
async def test_create_album(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    album: dict,
) -> None:
    """Should return Created, location header."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=ID,
    )

    request_body = album

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 201
        assert f"/albums/{ID}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_album_by_g_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture, album: dict
) -> None:
    """Should return OK, and a body containing one album."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    g_id = (
        "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK"
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_g_id",
        return_value={"id": ID} | album,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/albums?gId={g_id}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(album) is dict
        assert body["g_id"] == g_id
        assert body["place"] == album["place"]
        assert body["last_sync_time"] == album["last_sync_time"]


@pytest.mark.integration
async def test_get_album_by_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture, album: dict
) -> None:
    """Should return OK, and a body containing one album."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID} | album,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get(f"/albums/{ID}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(album) is dict
        assert body["id"] == ID
        assert body["place"] == album["place"]
        assert body["last_sync_time"] == album["last_sync_time"]


@pytest.mark.integration
async def test_update_album_by_id(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    album: dict,
) -> None:
    """Should return No Content."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID} | album,  # type: ignore
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value={"id": ID} | album,  # type: ignore
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    new_name = "Oslo Skagen sprint Oppdatert"
    request_body = deepcopy(album)
    request_body["id"] = ID
    request_body["place"] = new_name

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/albums/{ID}", headers=headers, json=request_body)
        assert resp.status == 204


@pytest.mark.integration
async def test_get_all_albums(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_all_albums",
        return_value=[
            {
                "g_id": "google_album_id",
                "id": ID,
                "place": "Oslo Skagen Sprint",
                "finish_line": False,
            }
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get("/albums")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        albums = await resp.json()
        assert type(albums) is list
        assert len(albums) > 0
        assert ID == albums[0]["id"]


@pytest.mark.integration
async def test_delete_album_by_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=ID,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.delete(f"/albums/{ID}", headers=headers)
        assert resp.status == 204


# Bad cases

# Mandatory properties missing at create and update:
@pytest.mark.integration
async def test_create_album_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=ID,
    )
    request_body = {"optional_property": "Optional_property"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_create_album_with_input_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=ID,
    )
    request_body = {"id": ID, "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_create_album_adapter_fails(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 400 HTTPBadRequest."""
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=None,
    )
    request_body = {"g_id": "google_album_id", "place": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 400


@pytest.mark.integration
async def test_update_album_by_id_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": ID, "optional_property": "Optional_property"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/albums/{ID}", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_update_album_by_id_different_id_in_body(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": "different_id", "place": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/albums/{ID}", headers=headers, json=request_body)
        assert resp.status == 422


# Unauthorized cases:


@pytest.mark.integration
async def test_create_album_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=ID,
    )

    request_body = {"place": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 401


@pytest.mark.integration
async def test_update_album_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value={"id": ID, "place": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
    }

    request_body = {"id": ID, "place": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.put(f"/albums/{ID}", headers=headers, json=request_body)
        assert resp.status == 401


@pytest.mark.integration
async def test_delete_album_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=ID,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.delete(f"/albums/{ID}")
        assert resp.status == 401


# Forbidden:
@pytest.mark.integration
async def test_create_album_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.albums_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.create_album",
        return_value=ID,
    )
    request_body = {"place": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=403)
        resp = await client.post("/albums", headers=headers, json=request_body)
        assert resp.status == 403


# NOT FOUND CASES:


@pytest.mark.integration
async def test_get_album_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get(f"/albums/{ID}")
        assert resp.status == 404


@pytest.mark.integration
async def test_update_album_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.update_album",
        return_value=None,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {
        "id": ID,
        "g_id": "google_album_id",
        "place": "Oslo Skagen sprint Oppdatert",
    }

    ID = "does-not-exist"
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.put(f"/albums/{ID}", headers=headers, json=request_body)
        assert resp.status == 404


@pytest.mark.integration
async def test_delete_album_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.get_album_by_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.albums_adapter.AlbumsAdapter.delete_album",
        return_value=None,
    )

    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.delete(f"/albums/{ID}", headers=headers)
        assert resp.status == 404
