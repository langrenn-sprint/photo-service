"""Resource module for photos resources."""
import json
import logging
import os

from aiohttp import hdrs
from aiohttp.web import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPUnprocessableEntity,
    Response,
    View,
)
from dotenv import load_dotenv
from multidict import MultiDict

from photo_service.adapters import UsersAdapter
from photo_service.models import Photo
from photo_service.services import (
    IllegalValueException,
    PhotoNotFoundException,
    PhotosService,
)
from .utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class PhotosView(View):
    """Class representing photos resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        if "gId" in self.request.rel_url.query:
            g_id = self.request.rel_url.query["gId"]
            photo = await PhotosService.get_photo_by_g_id(db, g_id)
            body = photo.to_json()
        else:
            if "raceclass" in self.request.rel_url.query:
                raceclass = self.request.rel_url.query["raceclass"]
                photos = await PhotosService.get_photos_by_raceclass(db, raceclass)
            else:
                photos = await PhotosService.get_all_photos(db)
            _list = []
            for _e in photos:
                _list.append(_e.to_dict())
            if "limit" in self.request.rel_url.query:
                limit = int(self.request.rel_url.query["limit"])
                limited_list = []
                i = 0
                # keep only the select starred photos, newest first
                for photo in reversed(_list):  # type: ignore
                    if i < limit:
                        if photo["starred"]:  # type: ignore
                            limited_list.append(photo)
                            i += 1
                    else:
                        break
                else:
                    # if needed select latest ustarred photos
                    for photo in reversed(_list):  # type: ignore
                        if i < limit:
                            if not photo["starred"]:  # type: ignore
                                limited_list.append(photo)
                                i += 1
                        else:
                            break
                body = json.dumps(limited_list, default=str, ensure_ascii=False)
            else:
                body = json.dumps(_list, default=str, ensure_ascii=False)
        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(f"Got create request for photo {body} of type {type(body)}")
        try:
            photo = Photo.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            photo_id = await PhotosService.create_photo(db, photo)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if photo_id:
            logging.debug(f"inserted document with photo_id {photo_id}")
            headers = MultiDict([(hdrs.LOCATION, f"{BASE_URL}/photos/{photo_id}")])

            return Response(status=201, headers=headers)
        raise HTTPBadRequest() from None


class PhotoView(View):
    """Class representing a single photo resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]

        photo_id = self.request.match_info["photoId"]
        logging.debug(f"Got get request for photo {photo_id}")

        try:
            photo = await PhotosService.get_photo_by_id(db, photo_id)
        except PhotoNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        logging.debug(f"Got photo: {photo}")
        body = photo.to_json()
        return Response(status=200, body=body, content_type="application/json")

    async def put(self) -> Response:
        """Put route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        photo_id = self.request.match_info["photoId"]
        logging.debug(f"Got request-body {body} for {photo_id} of type {type(body)}")
        body = await self.request.json()
        logging.debug(f"Got put request for photo {body} of type {type(body)}")
        try:
            photo = Photo.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            await PhotosService.update_photo(db, photo_id, photo)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        except PhotoNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        photo_id = self.request.match_info["photoId"]
        logging.debug(f"Got delete request for photo {photo_id}")

        try:
            await PhotosService.delete_photo(db, photo_id)
        except PhotoNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)
