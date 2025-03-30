"""Integration test cases for the photos route."""

import os
from copy import deepcopy
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
USERS_HOST_PORT = os.getenv("USERS_HOST_PORT", "8080")


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
async def photo() -> dict:
    """Photo object for testing."""
    return {
        "name": "IMG_6291.JPG",
        "is_photo_finish": True,
        "is_start_registration": False,
        "starred": False,
        "confidence": 0,
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "creation_time": "2022-03-05T06:41:52",
        "information": "Test photo for sprint",
        "race_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "raceclass": "K-Jr",
        "biblist": [2, 4],
        "clublist": ["Kjelsås", "Lyn"],
        "g_id": "APU9jkgGt2_roOwf_2g9UbOwRUg6OSVG4C9GZK",
        "g_product_url": "https://photos.google.com/G4C9GZK",
        "g_base_url": "https://storage.googleapis.com/langrenn-sprint/result3.jpg",
        "ai_information": {"persons": "3", "numbers": [5], "texts": ["LYN"]},
    }


@pytest.fixture
async def starred_photo() -> dict:
    """Photo object for testing."""
    return {
        "name": "IMG_6292.JPG",
        "is_photo_finish": True,
        "is_start_registration": False,
        "starred": True,
        "confidence": 0,
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "creation_time": "2022-03-05T06:51:52",
        "information": "Test starred photo for sprint",
        "race_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "raceclass": "K-Jr",
        "biblist": [2, 4, 6],
        "clublist": ["Kjelsås", "Lyn"],
        "g_id": "APU9jkgGt2_roOwf_2g9UbOwRUg6OSVG4C9GZS",
        "g_product_url": "https://photos.google.com/G4C9GZS",
        "g_base_url": "https://storage.googleapis.com/langrenn-sprint/result3.jpg",
        "ai_information": {"persons": "3", "numbers": [2], "texts": ["LYN"]},
    }


@pytest.mark.integration
async def test_create_photo(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    photo: dict,
    starred_photo: dict,
) -> None:
    """Should return Created, location header."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=p_id,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=p_id,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    request_body = photo
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.CREATED
        assert f"/photos/{p_id}" in resp.headers[hdrs.LOCATION]

    request_body = starred_photo
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.CREATED
        assert f"/photos/{p_id}" in resp.headers[hdrs.LOCATION]


@pytest.mark.integration
async def test_get_photo_by_g_base_url(
    client: _TestClient, mocker: MockFixture, token: MockFixture, photo: dict
) -> None:
    """Should return OK, and a body containing one photo."""
    g_base_url = "https://storage.googleapis.com/langrenn-sprint/result3.jpg"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_g_base_url",
        return_value={"g_base_url": g_base_url} | photo,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/photos?gBaseUrl={g_base_url}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(photo) is dict
        assert body["g_base_url"] == g_base_url
        assert body["name"] == photo["name"]
        assert body["creation_time"] == photo["creation_time"]
        assert body["information"] == photo["information"]


@pytest.mark.integration
async def test_get_photo_by_g_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture, photo: dict
) -> None:
    """Should return OK, and a body containing one photo."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    g_id = "APU9jkgGt2_roOwf_2g9UbOwRUg6OSVG4C9GZK"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_g_id",
        return_value={"id": p_id} | photo,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/photos?gId={g_id}")
        assert resp.status == HTTPStatus.OK
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
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id} | photo,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.get(f"/photos/{p_id}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        body = await resp.json()
        assert type(photo) is dict
        assert body["id"] == p_id
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
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id} | photo,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value={"id": p_id} | photo,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    new_name = "Oslo Skagen sprint Oppdatert"
    request_body = deepcopy(photo)
    request_body["id"] = p_id
    request_body["name"] = new_name

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.put(f"/photos/{p_id}", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.NO_CONTENT


@pytest.mark.integration
async def test_get_all_photos(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_all_photos",
        return_value=[{"id": p_id, "name": "Oslo Skagen Sprint", "finish_line": False}],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get("/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert len(photos) > 0
        assert p_id == photos[0]["id"]


@pytest.mark.integration
async def test_get_starred_photos(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photos_starred",
        return_value=[
            {"id": p_id, "name": "Oslo Skagen Sprint2", "starred": True},
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get("/photos?starred=true")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert len(photos) == 1
        assert photos[0]["starred"] is True


@pytest.mark.integration
async def test_get_number_of_photos(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_all_photos",
        return_value=[
            {"id": p_id, "name": "Oslo Skagen Sprint", "starred": False},
            {"id": "starred", "name": "Oslo Skagen Sprint2", "starred": True},
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(
            "/photos?eventId=1e95458c-e000-4d8b-beda-f860c77fd758&limit=2"
        )
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert photos[0]["id"] == "starred"
        assert p_id == photos[1]["id"]


@pytest.mark.integration
async def test_get_photos_by_raceclass(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    raceclass = "K-Jr"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photos_by_raceclass",
        return_value=[
            {
                "id": p_id,
                "name": "Oslo Skagen Sprint",
                "finish_line": False,
                "raceclass": raceclass,
            }
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/photos?eventId={event_id}&raceclass={raceclass}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert len(photos) > 0
        assert raceclass == photos[0]["raceclass"]


@pytest.mark.integration
async def test_get_photos_by_race_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    race_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photos_by_race_id",
        return_value=[
            {
                "id": p_id,
                "name": "Oslo Skagen Sprint",
                "finish_line": False,
                "race_id": race_id,
            }
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(f"/photos?raceId={race_id}")
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert race_id == photos[0]["race_id"]


@pytest.mark.integration
async def test_get_starred_photos_by_raceclass(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return OK and a valid json body."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "1e95458c-e000-4d8b-beda-f860c77fd758"
    raceclass = "K-Jr"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photos_starred_by_raceclass",
        return_value=[
            {
                "id": p_id,
                "name": "Oslo Skagen Sprint",
                "finish_line": False,
                "raceclass": raceclass,
                "starred": True,
            }
        ],
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.get(
            f"/photos?event_id={event_id}&raceclass={raceclass}&starred=true"
        )
        assert resp.status == HTTPStatus.OK
        assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
        photos = await resp.json()
        assert type(photos) is list
        assert len(photos) > 0
        assert raceclass == photos[0]["raceclass"]
        assert photos[0]["starred"] is True


@pytest.mark.integration
async def test_delete_photo_by_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return No Content."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.delete_photo",
        return_value=p_id,
    )
    headers = {
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.delete(f"/photos/{p_id}", headers=headers)
        assert resp.status == HTTPStatus.NO_CONTENT


# Bad cases


# Mandatory properties missing at create and update:
@pytest.mark.integration
async def test_create_photo_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=p_id,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=p_id,
    )
    request_body = {"optional_property": "Optional_property"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
async def test_create_photo_with_input_id(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=p_id,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=p_id,
    )
    request_body = {"id": p_id, "name": "Oslo Skagen sprint Oppdatert"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


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
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.BAD_REQUEST


@pytest.mark.integration
async def test_update_photo_by_id_missing_mandatory_property(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=p_id,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": p_id, "optional_property": "Optional_property"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.put(f"/photos/{p_id}", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.integration
async def test_update_photo_by_id_different_id_in_body(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 422 HTTPUnprocessableEntity."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=p_id,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    request_body = {"id": "different_id", "name": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.put(f"/photos/{p_id}", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


# Unauthorized cases:


@pytest.mark.integration
async def test_create_photo_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=p_id,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=p_id,
    )

    request_body = {"name": "Oslo Skagen sprint"}
    headers = MultiDict([(hdrs.CONTENT_TYPE, "application/json")])

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=401)

        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
async def test_update_photo_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value={"id": p_id, "name": "Oslo Skagen Sprint"},
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.update_photo",
        return_value=p_id,
    )

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
    }

    request_body = {"id": p_id, "name": "Oslo Skagen sprint Oppdatert"}

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=401)

        resp = await client.put(f"/photos/{p_id}", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
async def test_delete_photo_by_id_no_authorization(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401 Unauthorized."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.delete_photo",
        return_value=p_id,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=401)

        resp = await client.delete(f"/photos/{p_id}")
        assert resp.status == HTTPStatus.UNAUTHORIZED


# Forbidden:
@pytest.mark.integration
async def test_create_photo_insufficient_role(
    client: _TestClient, mocker: MockFixture, token_unsufficient_role: MockFixture
) -> None:
    """Should return 403 Forbidden."""
    p_id = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    mocker.patch(
        "photo_service.services.photos_service.create_id",
        return_value=p_id,
    )
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.create_photo",
        return_value=p_id,
    )
    request_body = {"name": "Oslo Skagen sprint"}
    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=403)
        resp = await client.post("/photos", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.FORBIDDEN


# NOT FOUND CASES:


@pytest.mark.integration
async def test_get_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    p_id = "does-not-exist"
    mocker.patch(
        "photo_service.adapters.photos_adapter.PhotosAdapter.get_photo_by_id",
        return_value=None,
    )

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)

        resp = await client.get(f"/photos/{p_id}")
        assert resp.status == HTTPStatus.NOT_FOUND


@pytest.mark.integration
async def test_update_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    p_id = "does-not-exist"
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

    p_id = "does-not-exist"
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.put(f"/photos/{p_id}", headers=headers, json=request_body)
        assert resp.status == HTTPStatus.NOT_FOUND


@pytest.mark.integration
async def test_delete_photo_not_found(
    client: _TestClient, mocker: MockFixture, token: MockFixture
) -> None:
    """Should return 404 Not found."""
    p_id = "does-not-exist"
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
        m.post(f"http://{USERS_HOST_SERVER}:{USERS_HOST_PORT}/authorize", status=204)
        resp = await client.delete(f"/photos/{p_id}", headers=headers)
        assert resp.status == HTTPStatus.NOT_FOUND
