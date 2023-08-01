"""Resource module for video_events."""
import json
import os

from aiohttp.web import (
    HTTPBadRequest,
    Response,
    View,
)
from dotenv import load_dotenv

from photo_service.adapters import UsersAdapter, VideoEventsAdapter
from photo_service.services import AzureServiceBusService
from .utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class VideoEventsView(View):
    """Class representing video_events resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        try:
            event_id = self.request.rel_url.query["eventId"]
        except Exception as e:
            raise HTTPBadRequest(reason="Mandatory param is missing - eventId.") from e

        # get all video_events
        video_events = await VideoEventsAdapter.get_all_video_events(db, event_id)
        list = []
        for _e in video_events:
            list.append(_e)
        body = json.dumps(list, default=str, ensure_ascii=False)

        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        try:
            event_id = self.request.rel_url.query["eventId"]
            queue_name = self.request.rel_url.query["queueName"]
        except Exception as e:
            raise HTTPBadRequest(
                reason="Mandatory param is missing - eventId/queueName."
            ) from e
        response_list = await AzureServiceBusService.receive_messages(
            db, event_id, queue_name
        )
        # convert response from list to json
        response = f"Hentet {len(response_list)} meldinger fra {queue_name}"

        return Response(status=201, body=response, content_type="application/json")
