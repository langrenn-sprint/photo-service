"""Resource module for status resources."""
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

from photo_service.adapters import StatusAdapter, UsersAdapter
from photo_service.services import (
    IllegalValueException,
)
from photo_service.utils.jwt_utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class StatusView(View):
    """Class representing status resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        type = self.request.rel_url.query["type"]
        event_id = self.request.rel_url.query["event_id"]

        status = await StatusAdapter.get_status(db, type, event_id)
        body = json.dumps(status)
        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "status-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(f"Got create request for status {body} of type {type(body)}")

        try:
            status_id = await StatusAdapter.create_status(db, body)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if status_id:
            logging.debug(f"inserted document with status_id {status_id}")
            headers = MultiDict([(hdrs.LOCATION, f"{BASE_URL}/status/{status_id}")])

            return Response(status=201, headers=headers)
        raise HTTPBadRequest() from None

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "status-admin"])
        except Exception as e:
            raise e from e

        status_id = self.request.match_info["id"]
        logging.debug(f"Got delete request for status {status_id}")

        try:
            await StatusAdapter.delete_status(db, status_id)
        except IllegalValueException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)
