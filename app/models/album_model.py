"""Album model module."""

from pydantic import BaseModel

from .changelog import Changelog


class Album(BaseModel):
    """Model with details about a synced album."""

    g_id: str
    is_photo_finish: bool = False
    is_start_registration: bool = False
    sync_on: bool = False
    event_id: str | None = None
    camera_position: str | None = None
    changelog: list[Changelog] | None = None
    cover_photo_url: str | None = None
    id: str | None = None
    last_sync_time: str | None = None
    place: str | None = None
    title: str | None = None
