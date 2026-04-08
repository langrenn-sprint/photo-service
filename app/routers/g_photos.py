"""Router module for Google Photos resources."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services import GooglePhotosService

router = APIRouter()


def _extract_token(request: Request) -> str | None:
    """Extract token from Authorization header."""
    authorization = request.headers.get("authorization")
    if authorization:
        return str.replace(str(authorization), "Bearer ", "")
    return None


@router.get("/g_photos")
async def get_g_photos(request: Request) -> Response:
    """Get Google Photos route function."""
    g_token = str(_extract_token(request))
    photos = await GooglePhotosService.get_media_items(g_token, None)
    body = json.dumps(photos, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")


@router.get("/g_photos/{albumId}")
async def get_g_photos_by_album(albumId: str, request: Request) -> Response:
    """Get Google Photos by album route function."""
    g_token = str(_extract_token(request))
    photos = await GooglePhotosService.get_media_items(g_token, albumId)
    body = json.dumps(photos, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")
