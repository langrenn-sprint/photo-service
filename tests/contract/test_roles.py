"""Contract test cases for the role model (event-service-gui#215).

Users with each role are created in user-service and log in, so the tests use
real tokens with the role names user-service hands out. The tests check the
whole role model against the running service, and with real data that
result-admin may edit photos (raceday), while only admin may change an album.
"""

import os
import re
from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Any
from urllib.parse import urlparse

import motor.motor_asyncio
import pytest
from httpx import AsyncClient, Response

from app.utils import db_utils
from tests.role_model import (
    ADMIN,
    RESULT_ADMIN,
    ROLES,
    access_cases,
)

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _check(response: Response, expected: HTTPStatus, action: str) -> Response:
    assert response.status_code == expected, (
        f"{action}: got {response.status_code}, {response.text[:500]}"
    )
    return response


def _url(http_service: str, response: Response) -> str:
    # Location is an absolute URL with the service's own host name:
    return http_service + urlparse(response.headers["Location"]).path


async def _login(
    client: AsyncClient, users_url: str, username: str, password: str
) -> str:
    response = await client.post(
        f"{users_url}/login", json={"username": username, "password": password}
    )
    return _check(response, HTTPStatus.OK, f"login {username}").json()["token"]


@pytest.fixture(scope="module", autouse=True)
async def clear_db(db_address: dict[str, Any]) -> AsyncGenerator:
    """Clear db before and after tests."""
    mongo = motor.motor_asyncio.AsyncIOMotorClient(
        **db_address, username=DB_USER, password=DB_PASSWORD
    )
    await db_utils.drop_db_and_recreate_indexes(mongo, DB_NAME)
    yield
    await db_utils.drop_db(mongo, DB_NAME)


@pytest.fixture(scope="module")
async def tokens(http_service: Any, users_url: str, clear_db: Any) -> dict[str, str]:
    """Log in as admin, create a user for each other role, and log in as them."""
    _ = http_service, clear_db  # the service is up, and the db is cleared first
    async with AsyncClient() as client:
        admin_token = await _login(
            client,
            users_url,
            os.environ["ADMIN_USERNAME"],
            os.environ["ADMIN_PASSWORD"],
        )
        tokens = {ADMIN: admin_token}
        for role in ROLES:
            if role == ADMIN:
                continue
            username = f"{role}@example.com"
            response = await client.post(
                f"{users_url}/users",
                headers=_auth(admin_token),
                json={"username": username, "password": "secret", "role": role},
            )
            _check(response, HTTPStatus.CREATED, f"create user with role {role}")
            tokens[role] = await _login(client, users_url, username, "secret")
    return tokens


# --- The role model, with real tokens -------------------------------------------


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
@pytest.mark.parametrize(("method", "path", "role", "allowed"), access_cases(ROLES))
async def test_write_access(  # noqa: PLR0913
    http_service: str,
    tokens: dict[str, str],
    method: str,
    path: str,
    role: str,
    *,
    allowed: bool,
) -> None:
    """Allowed roles pass the role check, the others get 403.

    The role check runs before validation. With an empty body, or an id that
    does not exist, an allowed role gets an error other than 401 or 403, and
    nothing is changed.
    """
    url = http_service + re.sub(r"\{\w+\}", "not-a-uuid", path)
    async with AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers=_auth(tokens[role]),
            json=None if method == "DELETE" else {},
        )
    if allowed:
        assert response.status_code not in (
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN,
        ), f"{method} {path} as {role}: got {response.status_code}"
    else:
        _check(response, HTTPStatus.FORBIDDEN, f"{method} {path} as {role}")


# --- Scenario ---------------------------------------------------------------


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_only_admin_changes_an_album(
    http_service: str, tokens: dict[str, str]
) -> None:
    """Of the roles in user-service, only admin may change an album."""
    album = {
        "camera_position": "right",
        "changelog": [],
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "g_id": "rolletest",
        "is_photo_finish": True,
        "is_start_registration": False,
        "last_sync_time": "2022-09-25T16:41:52",
        "place": "finish",
        "sync_on": False,
        "title": "Rolletest",
        "cover_photo_url": "",
    }
    other_roles = [role for role in ROLES if role != ADMIN]
    async with AsyncClient() as client:
        for role in other_roles:
            response = await client.post(
                f"{http_service}/albums", headers=_auth(tokens[role]), json=album
            )
            _check(response, HTTPStatus.FORBIDDEN, f"create as {role}")

        response = await client.post(
            f"{http_service}/albums", headers=_auth(tokens[ADMIN]), json=album
        )
        url = _url(http_service, _check(response, HTTPStatus.CREATED, "create"))
        album = _check(await client.get(url), HTTPStatus.OK, "get").json()

        for role in other_roles:
            changed = {**album, "title": f"Endret av {role}"}
            response = await client.put(url, headers=_auth(tokens[role]), json=changed)
            _check(response, HTTPStatus.FORBIDDEN, f"update as {role}")
            response = await client.delete(url, headers=_auth(tokens[role]))
            _check(response, HTTPStatus.FORBIDDEN, f"delete as {role}")

        assert _check(await client.get(url), HTTPStatus.OK, "get").json() == album
        response = await client.delete(url, headers=_auth(tokens[ADMIN]))
        _check(response, HTTPStatus.NO_CONTENT, "delete as admin")


@pytest.mark.contract
@pytest.mark.asyncio(scope="module")
async def test_result_admin_edits_photos(
    http_service: str, tokens: dict[str, str]
) -> None:
    """result-admin may create, update and delete photos; the others get 403."""
    photo = {
        "name": "IMG_ROLLETEST.JPG",
        "is_photo_finish": True,
        "is_start_registration": False,
        "confidence": 0,
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "creation_time": "2026-11-06T12:01:02",
        "information": {"description": "Rolletest"},
        "race_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "raceclass": "G11",
        "biblist": [2, 4],
        "clublist": ["Kjelsås", "Lyn"],
        "g_id": "rolletest-photo",
        "g_product_url": "https://photos.google.com/rolletest",
        "g_base_url": "https://lh3.googleusercontent.com/rolletest",
        "ai_information": {"persons": "2", "numbers": [2, 4], "texts": []},
    }
    other_roles = [role for role in ROLES if role not in (ADMIN, RESULT_ADMIN)]
    token = tokens[RESULT_ADMIN]
    async with AsyncClient() as client:
        for role in other_roles:
            response = await client.post(
                f"{http_service}/photos", headers=_auth(tokens[role]), json=photo
            )
            _check(response, HTTPStatus.FORBIDDEN, f"create photo as {role}")

        response = await client.post(
            f"{http_service}/photos", headers=_auth(token), json=photo
        )
        url = _url(http_service, _check(response, HTTPStatus.CREATED, "create"))
        photo = _check(await client.get(url), HTTPStatus.OK, "get").json()

        for role in other_roles:
            changed = {**photo, "biblist": [9]}
            response = await client.put(url, headers=_auth(tokens[role]), json=changed)
            _check(response, HTTPStatus.FORBIDDEN, f"update photo as {role}")
            response = await client.delete(url, headers=_auth(tokens[role]))
            _check(response, HTTPStatus.FORBIDDEN, f"delete photo as {role}")

        # On raceday, result-admin corrects the bibs on a photo:
        response = await client.put(
            url, headers=_auth(token), json={**photo, "biblist": [4]}
        )
        _check(response, HTTPStatus.NO_CONTENT, "update photo as result-admin")
        updated = _check(await client.get(url), HTTPStatus.OK, "get").json()
        assert updated["biblist"] == [4]

        response = await client.delete(url, headers=_auth(token))
        _check(response, HTTPStatus.NO_CONTENT, "delete photo as result-admin")
