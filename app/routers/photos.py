"""Router module for photos resources."""

import json
import logging
import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.authorization import RoleChecker, UserRole
from app.models import Photo
from app.services import (
    IllegalValueError,
    PhotoNotFoundError,
    PhotosService,
)

HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"

router = APIRouter()


class PhotosQueryParams(BaseModel):
    """Query parameters for filtering photos."""

    event_id: str = Field(default="", alias="eventId")
    g_id: str | None = Field(default=None, alias="gId")
    g_base_url: str | None = Field(default=None, alias="gBaseUrl")
    raceclass: str | None = None
    race_id: str | None = Field(default=None, alias="raceId")
    starred: bool = False
    limit: int | None = None


@router.get("/photos")
async def get_photos(params: Annotated[PhotosQueryParams, Query()]) -> Response:
    """Get photos route function."""
    if params.g_id is not None:
        photo = await PhotosService.get_photo_by_g_id(params.g_id)
        body = photo.model_dump_json()
        return Response(status_code=200, content=body, media_type="application/json")
    if params.g_base_url is not None:
        photo = await PhotosService.get_photo_by_g_base_url(params.g_base_url)
        body = photo.model_dump_json()
        return Response(status_code=200, content=body, media_type="application/json")

    if params.raceclass is not None:
        if params.starred:
            photos = await PhotosService.get_photos_starred_by_raceclass(params.event_id, params.raceclass)
        else:
            photos = await PhotosService.get_photos_by_raceclass(params.event_id, params.raceclass)
    elif params.race_id is not None:
        photos = await PhotosService.get_photos_by_race_id(params.race_id)
    elif params.starred:
        photos = await PhotosService.get_photos_starred(params.event_id)
    else:
        photos = await PhotosService.get_all_photos(params.event_id)

    _list = [p.model_dump() for p in photos]

    if params.limit is not None:
        limited_list: list = []
        i = 0
        for photo_dict in reversed(_list):
            if i < params.limit:
                if photo_dict["starred"]:
                    limited_list.append(photo_dict)
                    i += 1
            else:
                break
        else:
            for photo_dict in reversed(_list):
                if i < params.limit:
                    if not photo_dict["starred"]:
                        limited_list.append(photo_dict)
                        i += 1
                else:
                    break
        body = json.dumps(limited_list, default=str, ensure_ascii=False)
    else:
        body = json.dumps(_list, default=str, ensure_ascii=False)

    return Response(status_code=200, content=body, media_type="application/json")


@router.post(
    "/photos",
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def create_photo(photo: Photo) -> Response:
    """Create photo route function."""
    logging.debug(f"Got create request for photo {photo} of type {type(photo)}")
    try:
        photo_id = await PhotosService.create_photo(photo)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    if photo_id:
        logging.debug(f"inserted document with photo_id {photo_id}")
        return Response(
            status_code=201,
            headers={"Location": f"{BASE_URL}/photos/{photo_id}"},
        )
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST) from None


@router.get("/photos/{photo_id}")
async def get_photo(photo_id: str) -> Response:
    """Get photo by id route function."""
    logging.debug(f"Got get request for photo {photo_id}")
    try:
        photo = await PhotosService.get_photo_by_id(photo_id)
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    logging.debug(f"Got photo: {photo}")
    body = photo.model_dump_json()
    return Response(status_code=200, content=body, media_type="application/json")


@router.put(
    "/photos/{photo_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def update_photo(photo_id: str, photo: Photo) -> Response:
    """Update photo route function."""
    logging.debug(f"Got put request for photo {photo} of type {type(photo)}")
    try:
        await PhotosService.update_photo(photo_id, photo)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.delete(
    "/photos/{photo_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def delete_photo(photo_id: str) -> Response:
    """Delete photo route function."""
    logging.debug(f"Got delete request for photo {photo_id}")
    try:
        await PhotosService.delete_photo(photo_id)
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
