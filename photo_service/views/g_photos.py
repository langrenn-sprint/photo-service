"""Resource module for photos resources."""
import json
import logging

from aiohttp.web import (
    Response,
    View,
)

from photo_service.services import (
    GooglePhotosService,
)
from .utils import extract_token_from_request


class GooglePhotosView(View):
    """Class representing photos resource."""

    async def get(self) -> Response:
        """Get route function."""
        g_token = str(extract_token_from_request(self.request))

        try:
            album_id = self.request.match_info["albumId"]
            logging.debug(f"Got get request for photos in album {album_id}")
        except Exception:
            album_id = None

        photos = await GooglePhotosService.get_media_items(g_token, album_id)

        body = json.dumps(photos, default=str, ensure_ascii=False)
        return Response(status=200, body=body, content_type="application/json")
