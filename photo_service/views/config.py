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

from photo_service.adapters import UsersAdapter
from photo_service.models import Config
from photo_service.services import (
    ConfigNotFoundError,
    ConfigService,
    IllegalValueError,
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

        config = await ConfigService.get_config_by_key(db, event_id, key)
        body = config.to_json()
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
            config = Config.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            config_id = await ConfigService.create_config(db, config)
        except IllegalValueError as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if config_id:
            logging.debug(f"inserted document with config_id {config_id}")
            headers = MultiDict([(hdrs.LOCATION, f"{BASE_URL}/config/{config_id}")])

            return Response(status=201, headers=headers)
        raise HTTPBadRequest from None

    async def put(self) -> Response:
        """Put route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "config-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(f"Got put request for album {body} of type {type(body)}")
        try:
            config = Config.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            await ConfigService.update_config(db, config)
        except IllegalValueError as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        except ConfigNotFoundError as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "config-admin"])
        except Exception as e:
            raise e from e

        config_id = self.request.match_info["configId"]
        logging.debug(f"Got delete request for config {config_id}")

        try:
            await ConfigService.delete_config(db, config_id)
        except IllegalValueError as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)


class ConfigsView(View):
    """Class representing configs resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        if "eventId" in self.request.rel_url.query:
            event_id = self.request.rel_url.query["eventId"]
            configs = await ConfigService.get_all_configs(db, event_id)
        else:
            configs = await ConfigService.get_all_configs(db, None)

        _list = [_e.to_dict() for _e in configs]
        body = json.dumps(_list, default=str, ensure_ascii=False)
        return Response(status=200, body=body, content_type="application/json")
