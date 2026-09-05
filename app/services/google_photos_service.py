"""Module for google photos service."""

import logging
import os
from http import HTTPStatus

import httpx
from fastapi import HTTPException

GOOGLE_PHOTO_SERVER = os.getenv(
    "GOOGLE_PHOTO_SERVER", "https://photoslibrary.googleapis.com/v1"
)


class GooglePhotosService:
    """Class representing google photos."""

    @classmethod
    async def get_media_items(cls, token: str, album_id: str | None) -> dict:
        """Get all media items."""
        album_items = {}
        servicename = "get_album_items"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        request_body: dict = {}
        if album_id:
            request_body = {"albumId": album_id}
        async with httpx.AsyncClient() as session:
            resp = await session.post(
                f"{GOOGLE_PHOTO_SERVER}/mediaItems:search",
                headers=headers,
                json=request_body,
            )
            logging.debug(f"{servicename} - got response {resp.status_code}")
            if resp.status_code == HTTPStatus.OK:
                album_items = resp.json()
            else:
                body = resp.json()
                logging.error(f"{servicename} failed - {resp.status_code} - {body}")
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Error - {resp.status_code}: {body}.",
                )
        return album_items

    @classmethod
    async def get_albums(cls, token: str) -> dict:
        """Get all albums."""
        albums = {}
        servicename = "get_albums"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        async with httpx.AsyncClient() as session:
            resp = await session.get(f"{GOOGLE_PHOTO_SERVER}/albums", headers=headers)
            logging.debug(f"{servicename} - got response {resp.status_code}")
            if resp.status_code == HTTPStatus.OK:
                albums = resp.json()
            else:
                body = resp.json()
                logging.error(f"{servicename} failed - {resp.status_code} - {body}")
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Error - {resp.status_code}: {body}.",
                )
        return albums
