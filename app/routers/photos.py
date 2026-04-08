"""Router module for photos resources."""

import json
import logging
import os
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

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


@router.get("/photos")
async def get_photos(
    eventId: str = "",
    gId: str | None = None,
    gBaseUrl: str | None = None,
    raceclass: str | None = None,
    raceId: str | None = None,
    starred: bool = False,
    limit: int | None = None,
) -> Response:
    """Get photos route function."""
    if gId is not None:
        photo = await PhotosService.get_photo_by_g_id(gId)
        body = photo.model_dump_json()
        return Response(status_code=200, content=body, media_type="application/json")
    if gBaseUrl is not None:
        photo = await PhotosService.get_photo_by_g_base_url(gBaseUrl)
        body = photo.model_dump_json()
        return Response(status_code=200, content=body, media_type="application/json")

    if raceclass is not None:
        if starred:
            photos = await PhotosService.get_photos_starred_by_raceclass(eventId, raceclass)
        else:
            photos = await PhotosService.get_photos_by_raceclass(eventId, raceclass)
    elif raceId is not None:
        photos = await PhotosService.get_photos_by_race_id(raceId)
    elif starred:
        photos = await PhotosService.get_photos_starred(eventId)
    else:
        photos = await PhotosService.get_all_photos(eventId)

    _list = [p.model_dump() for p in photos]

    if limit is not None:
        limited_list: list = []
        i = 0
        for photo_dict in reversed(_list):
            if i < limit:
                if photo_dict["starred"]:
                    limited_list.append(photo_dict)
                    i += 1
            else:
                break
        else:
            for photo_dict in reversed(_list):
                if i < limit:
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


@router.get("/photos/{photoId}")
async def get_photo(photoId: str) -> Response:
    """Get photo by id route function."""
    logging.debug(f"Got get request for photo {photoId}")
    try:
        photo = await PhotosService.get_photo_by_id(photoId)
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    logging.debug(f"Got photo: {photo}")
    body = photo.model_dump_json()
    return Response(status_code=200, content=body, media_type="application/json")


@router.put(
    "/photos/{photoId}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def update_photo(photoId: str, photo: Photo) -> Response:
    """Update photo route function."""
    logging.debug(f"Got put request for photo {photo} of type {type(photo)}")
    try:
        await PhotosService.update_photo(photoId, photo)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.delete(
    "/photos/{photoId}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def delete_photo(photoId: str) -> Response:
    """Delete photo route function."""
    logging.debug(f"Got delete request for photo {photoId}")
    try:
        await PhotosService.delete_photo(photoId)
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
