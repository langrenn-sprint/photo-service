"""Integration test cases for the photos route."""
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
async def photo() -> dict:
    """An photo object for testing."""
    return {
        "name": "IMG_6291.JPG",
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "creation_time": "2022-03-05T06:41:52",
        "information": "Test photo for sprint",
        "race_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "raceclass": "K-Jr",
        "biblist": [2, 4],
        "clublist": ["Kjelsås", "Lyn"],
        "g_id": "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK",
        "g_product_url": "https://photos.google.com/G4C9GZK",
        "g_base_url": "https://lh3.googleusercontent.com/f_AEeh",
        "ai_information": {"persons": "3", "numbers": [5], "texts": ["LYN"]},
    }


@pytest.mark.integration
async def test_create_photo(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    photo: dict,
) -> None:
    """Should return Created, location header."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=ID,
    )

    request_body = photo

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 201
        assert f"/photos/{ID}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_photo_by_g_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture, photo: dict
) -> None:
    """Should return OK, and a body containing one photo."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    g_id = (
        "APU9jkgGt20Pq1SHqEjC1TiOuOliKbH5P64k_roOwf_sXKuY57KFCCQ2g9UbOwRUg6OSVG4C9GZK"
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_g_id",
        return_value={"id": ID} | photo,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get(f"/photos?gId={g_id}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(photo) is dict
        assert body["g_id"] == g_id
        assert body["name"] == photo["name"]
        assert body["creation_time"] == photo["creation_time"]
        assert body["information"] == photo["information"]


@pytest.mark.integration
async def test_get_photo_by_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture, photo: dict
) -> None:
    """Should return OK, and a body containing one photo."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID} | photo,  # type: ignore
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get(f"/photos/{ID}")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(photo) is dict
        assert body["id"] == ID
        assert body["name"] == photo["name"]
        assert body["creation_time"] == photo["creation_time"]
        assert body["information"] == photo["information"]


@pytest.mark.integration
async def test_update_photo_by_id(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    photo: dict,
) -> None:
    """Should return No Content."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID} | photo,  # type: ignore
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value={"id": ID} | photo,  # type: ignore
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    new_name = "Oslo Skagen sprint Oppdatert"
    request_body = deepcopy(photo)
    request_body["id"] = ID
    request_body["name"] = new_name

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/photos/{ID}", headers=headers, json=request_body)
        assert resp.status == 204


@pytest.mark.integration
async def test_get_all_photos(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_all_photos",
        return_value=[{"id": ID, "name": "Oslo Skagen Sprint"}],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.get("/photos")
        assert resp.status == 200
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert len(photos) > 0
        assert ID == photos[0]["id"]


@pytest.mark.integration
async def test_delete_photo_by_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.delete_photo",
        return_value=ID,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.delete(f"/photos/{ID}", headers=headers)
        assert resp.status == 204


# Bad cases

# Mandatory properties missing at create and update:
@pytest.mark.integration
async def test_create_photo_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=ID,
    )
    request_body = {"optional_property": "Optional_property"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_create_photo_with_input_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=ID,
    )
    request_body = {"id": ID, "name": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_create_photo_adapter_fails(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 400 HTTPBadRequest."""
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=None,
    )
    request_body = {"name": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 400


@pytest.mark.integration
async def test_update_photo_by_id_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": ID, "optional_property": "Optional_property"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/photos/{ID}", headers=headers, json=request_body)
        assert resp.status == 422


@pytest.mark.integration
async def test_update_photo_by_id_different_id_in_body(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": "different_id", "name": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.put(f"/photos/{ID}", headers=headers, json=request_body)
        assert resp.status == 422


# Unauthorized cases:


@pytest.mark.integration
async def test_create_photo_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=ID,
    )

    request_body = {"name": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 401


@pytest.mark.integration
async def test_update_photo_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": ID, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=ID,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
    }

    request_body = {"id": ID, "name": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.put(f"/photos/{ID}", headers=headers, json=request_body)
        assert resp.status == 401


@pytest.mark.integration
async def test_delete_photo_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.delete_photo",
        return_value=ID,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=401)

        resp = await client.delete(f"/photos/{ID}")
        assert resp.status == 401


# Forbidden:
@pytest.mark.integration
async def test_create_photo_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=ID,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=ID,
    )
    request_body = {"name": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=403)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == 403


# NOT FOUND CASES:


@pytest.mark.integration
async def test_get_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value=None,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)

        resp = await client.get(f"/photos/{ID}")
        assert resp.status == 404


@pytest.mark.integration
async def test_update_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=None,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {
        "id": "290e70d5-0933-4af0-bb53-1d705ba7eb95",
        "name": "Oslo Skagen sprint Oppdatert",
    }

    ID = "does-not-exist"
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.put(f"/photos/{ID}", headers=headers, json=request_body)
        assert resp.status == 404


@pytest.mark.integration
async def test_delete_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    ID = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value=None,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.delete_photo",
        return_value=None,
    )

    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.delete(f"/photos/{ID}", headers=headers)
        assert resp.status == 404
