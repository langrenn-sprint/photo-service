"""Resource module for albums resources."""
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
from photo_service.models import Album
from photo_service.services import (
    AlbumNotFoundException,
    AlbumsService,
    IllegalValueException,
)
from photo_service.utils.jwt_utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class AlbumsView(View):
    """Class representing albums resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        if "gId" in self.request.rel_url.query:
            g_id = self.request.rel_url.query["gId"]
            album = await AlbumsService.get_album_by_g_id(db, g_id)
            body = album.to_json()
        else:
            albums = await AlbumsService.get_all_albums(db)
            list = []
            for _e in albums:
                list.append(_e.to_dict())
            body = json.dumps(list, default=str, ensure_ascii=False)
        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "album-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(f"Got create request for album {body} of type {type(body)}")
        try:
            album = Album.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            album_id = await AlbumsService.create_album(db, album)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if album_id:
            logging.debug(f"inserted document with album_id {album_id}")
            headers = MultiDict([(hdrs.LOCATION, f"{BASE_URL}/albums/{album_id}")])

            return Response(status=201, headers=headers)
        raise HTTPBadRequest() from None


class AlbumView(View):
    """Class representing a single album resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]

        album_id = self.request.match_info["albumId"]
        logging.debug(f"Got get request for album {album_id}")

        try:
            album = await AlbumsService.get_album_by_id(db, album_id)
        except AlbumNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        logging.debug(f"Got album: {album}")
        body = album.to_json()
        return Response(status=200, body=body, content_type="application/json")

    async def put(self) -> Response:
        """Put route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "album-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        album_id = self.request.match_info["albumId"]
        logging.debug(f"Got request-body {body} for {album_id} of type {type(body)}")
        body = await self.request.json()
        logging.debug(f"Got put request for album {body} of type {type(body)}")
        try:
            album = Album.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            await AlbumsService.update_album(db, album_id, album)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        except AlbumNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "album-admin"])
        except Exception as e:
            raise e from e

        album_id = self.request.match_info["albumId"]
        logging.debug(f"Got delete request for album {album_id}")

        try:
            await AlbumsService.delete_album(db, album_id)
        except AlbumNotFoundException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)
