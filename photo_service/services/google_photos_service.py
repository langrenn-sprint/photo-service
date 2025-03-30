"""Module for google photos adapter."""

import logging
import os
from http import HTTPStatus
from typing import Any

from aiohttp import ClientSession, hdrs, web
from multidict import MultiDict

GOOGLE_PHOTO_SERVER = os.getenv(
    "GOOGLE_PHOTO_SERVER", "https://photoslibrary.googleapis.com/v1"
)
GOOGLE_PHOTO_SCOPE = os.getenv(
    "GOOGLE_PHOTO_SCOPE", "https://www.googleapis.com/auth/photoslibrary.readonly"
)
GOOGLE_PHOTO_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_PHOTO_CREDENTIALS_FILE", "/home/heming/github/photo_api_credentials.json"
)


class GooglePhotosService:
    """Class representing google photos."""

    @classmethod
    async def get_media_items(cls: Any, token: str, album_id: str | None) -> dict:
        """Get all albums."""
        album_items = {}
        servicename = "get_album_items"
        headers = MultiDict(
            [
                (hdrs.CONTENT_TYPE, "application/json"),
                (hdrs.AUTHORIZATION, f"Bearer {token}"),
            ]
        )
        request_body = {}
        if album_id:
            request_body = {"albumId": album_id}
        async with ClientSession() as session:
            async with session.post(
                f"{GOOGLE_PHOTO_SERVER}/mediaItems:search",
                headers=headers,
                json=request_body,
            ) as resp:
                logging.debug(f"{servicename} - got response {resp.status}")
                if resp.status == HTTPStatus.OK:
                    album_items = await resp.json()
                else:
                    body = await resp.json()
                    logging.error(f"{servicename} failed - {resp.status} - {body}")
                    raise web.HTTPBadRequest(reason=f"Error - {resp.status}: {body}.")
        return album_items

    @classmethod
    async def get_albums(cls: Any, token: str) -> dict:
        """Get all albums."""
        albums = {}
        servicename = "get_albums"
        headers = MultiDict(
            [
                (hdrs.CONTENT_TYPE, "application/json"),
                (hdrs.AUTHORIZATION, f"Bearer {token}"),
            ]
        )
        async with ClientSession() as session:
            async with session.get(
                f"{GOOGLE_PHOTO_SERVER}/albums", headers=headers
            ) as resp:
                logging.debug(f"{servicename} - got response {resp.status}")
                if resp.status == HTTPStatus.OK:
                    albums = await resp.json()
                else:
                    body = await resp.json()
                    logging.error(f"{servicename} failed - {resp.status} - {body}")
                    raise web.HTTPBadRequest(reason=f"Error - {resp.status}: {body}.")
        return albums
