"""Resource module for configs resources."""

import os
from typing import Any

from aiohttp.web import (
    Response,
    View,
)
from dotenv import load_dotenv

from photo_service.models import Config, Status
from photo_service.services import (
    ConfigService,
    StatusService,
)

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class UnitTestView(View):
    """Class representing unit test resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        try:
            domain = self.request.rel_url.query["domain"]
            action = int(self.request.rel_url.query["action"])
        except Exception as e:
            body = f"Usage - Use url params action and domain: {e}"
            return Response(status=400, body=body)

        if domain == "config":
            try:
                body = await test_config(db, action)
                return Response(status=201, body=body)
            except Exception as e:
                body = f"ERROR Config: {e}"
                return Response(status=500, body=body)
        elif domain == "status":
            try:
                body = await test_status(db, action)
                return Response(status=201, body=body)
            except Exception as e:
                body = f"ERROR Status: {e}"
                return Response(status=500, body=body)

        body = "Test domains: config, status"
        return Response(status=200, body=body)


async def test_config(db: Any, action: int) -> str:
    """Class representing unit test for config resource."""
    body = ""
    config_dict = {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "key": "photo_location",
        "value": "2024 Ragde-sprinten",
    }
    config = Config.from_dict(config_dict)

    if action == 0:
        body = "Config: 1-create,2-get-all,3-get-all-by-event,4-update,5-delete,6-get-by-key"
    elif action == 1:
        # create config
        result = await ConfigService.create_config(db, config)
        body = f"Config created: {result}"
    elif action == 2:
        # get all config
        result = await ConfigService.get_all_configs(db)  # type: ignore
        body = f"Configs: {result}"
    elif action == 3:
        # get all config by event
        event_id = config_dict["event_id"]
        result = await ConfigService.get_all_configs(db, event_id)  # type: ignore
        body = f"Configs by event: {result}"
    elif action == 4:
        # update config
        configs = await ConfigService.get_all_configs(db)
        new_config = configs[0]
        new_config.value = "DENNE ER OPPDATERT!"
        result = await ConfigService.update_config(db, new_config)  # type: ignore
        body = f"Config updated: {result} - {new_config}"
    elif action == 5:
        # delete config
        configs = await ConfigService.get_all_configs(db)
        new_config = configs[0]
        result = await ConfigService.delete_config(db, new_config.id)  # type: ignore
        body = f"Config deleted: {result} - {new_config}"
    elif action == 6:
        # get config by key
        event_id = config_dict["event_id"]
        key = config_dict["key"]
        result = await ConfigService.get_config_by_key(db, event_id, key)  # type: ignore
        body = f"Config: {result}"
    return body


async def test_status(db: Any, action: int) -> str:
    """Class representing unit test for status resource."""
    body = ""
    status_dict = {
        "event_id": "1e95458c-e000-4d8b-beda-f860c77fd758",
        "time": "2022-09-25T16:41:52",
        "type": "video_status",
        "message": "2022 Ragde-sprinten",
    }
    status = Status.from_dict(status_dict)

    if action == 0:
        body = "Status: 1-create,2-get-all,3-get-all-by-type,5-delete"
    elif action == 1:
        # create status
        result = await StatusService.create_status(db, status)
        body = f"Status created: {result}"
    elif action == 2:
        # get all status
        event_id = status_dict["event_id"]
        result = await StatusService.get_all_status(db, event_id, 25)  # type: ignore
        body = f"Statuses: {result}"
    elif action == 3:
        # get all status by type
        event_id = status_dict["event_id"]
        type = status_dict["type"]
        result = await StatusService.get_all_status_by_type(db, event_id, type, 25)  # type: ignore
        body = f"Statuses by type: {result}"
    elif action == 5:
        # delete status
        event_id = status_dict["event_id"]
        statuss = await StatusService.get_all_status(db, event_id, 1)
        new_status = statuss[0]
        result = await StatusService.delete_status(db, new_status.id)  # type: ignore
        body = f"Status deleted: {result} - {new_status}"
    return body
