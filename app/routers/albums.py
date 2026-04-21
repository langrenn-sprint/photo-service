"""Router module for albums resources."""

import json
import logging
import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.authorization import RoleChecker, UserRole
from app.models import Album
from app.services import (
    AlbumNotFoundError,
    AlbumsService,
    IllegalValueError,
)

HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"

router = APIRouter()


@router.get("/albums")
async def get_albums(
    g_id: Annotated[str | None, Query(alias="gId")] = None,
) -> Response:
    """Get albums route function."""
    if g_id is not None:
        album = await AlbumsService.get_album_by_g_id(g_id)
        body = album.model_dump_json()
        return Response(status_code=200, content=body, media_type="application/json")
    albums = await AlbumsService.get_all_albums()
    _list = [a.model_dump() for a in albums]
    body = json.dumps(_list, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")


@router.post(
    "/albums",
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.AlbumAdmin]))],
)
async def create_album(album: Album) -> Response:
    """Create album route function."""
    logging.debug(f"Got create request for album {album} of type {type(album)}")
    try:
        album_id = await AlbumsService.create_album(album)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    if album_id:
        logging.debug(f"inserted document with album_id {album_id}")
        return Response(
            status_code=201,
            headers={"Location": f"{BASE_URL}/albums/{album_id}"},
        )
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST) from None


@router.get("/albums/{album_id}")
async def get_album(album_id: str) -> Response:
    """Get album by id route function."""
    logging.debug(f"Got get request for album {album_id}")
    try:
        album = await AlbumsService.get_album_by_id(album_id)
    except AlbumNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    logging.debug(f"Got album: {album}")
    body = album.model_dump_json()
    return Response(status_code=200, content=body, media_type="application/json")


@router.put(
    "/albums/{album_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.AlbumAdmin]))],
)
async def update_album(album_id: str, album: Album) -> Response:
    """Update album route function."""
    logging.debug(f"Got put request for album {album} of type {type(album)}")
    try:
        await AlbumsService.update_album(album_id, album)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except AlbumNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.delete(
    "/albums/{album_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.AlbumAdmin]))],
)
async def delete_album(album_id: str) -> Response:
    """Delete album route function."""
    logging.debug(f"Got delete request for album {album_id}")
    try:
        await AlbumsService.delete_album(album_id)
    except AlbumNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
