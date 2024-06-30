"""Resource module for configs resources."""
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

from photo_service.adapters import ConfigAdapter, UsersAdapter
from photo_service.services import (
    IllegalValueException,
)
from photo_service.utils.jwt_utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class ConfigView(View):
    """Class representing configs resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        key = self.request.rel_url.query["key"]
        event_id = self.request.rel_url.query["eventId"]

        config = await ConfigAdapter.get_config_by_key(db, event_id, key)
        body = json.dumps(config)
        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "config-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(f"Got create request for config {body} of type {type(body)}")

        try:
            config_id = await ConfigAdapter.create_config(db, body)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if config_id:
            logging.debug(f"inserted document with config_id {config_id}")
            headers = MultiDict([(hdrs.LOCATION, f"{BASE_URL}/config/{config_id}")])

            return Response(status=201, headers=headers)
        raise HTTPBadRequest() from None

    async def put(self) -> Response:
        """Put route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "config-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()

        current_config = await ConfigAdapter.get_config_by_key(
            db, body["eventId"], body["key"]
        )
        if not current_config:
            raise HTTPNotFound(reason="Config not found")

        id = current_config["id"]
        try:
            await ConfigAdapter.update_config(db, id, body)
        except IllegalValueException as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        return Response(status=204)

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "config-admin"])
        except Exception as e:
            raise e from e

        config_id = self.request.match_info["id"]
        logging.debug(f"Got delete request for config {config_id}")

        try:
            await ConfigAdapter.delete_config(db, config_id)
        except IllegalValueException as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)


class ConfigsView(View):
    """Class representing configs resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        if "eventId" in self.request.rel_url.query:
            event_id = self.request.rel_url.query["eventId"]
            result = await ConfigAdapter.get_all_configs_by_event(db, event_id)
        else:
            result = await ConfigAdapter.get_all_configs(db)

        body = json.dumps(result)
        return Response(status=200, body=body, content_type="application/json")
