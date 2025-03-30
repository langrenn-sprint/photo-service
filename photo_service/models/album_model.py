"""Photo data class module."""

from dataclasses import dataclass, field
from datetime import time

from dataclasses_json import DataClassJsonMixin

from .changelog import Changelog


@dataclass
class Album(DataClassJsonMixin):
    """Data class with details about a sync-ed album."""

    g_id: str
    is_photo_finish: bool = False
    is_start_registration: bool = False
    sync_on: bool = False
    event_id: str | None = field(default=None)
    camera_position: str | None = field(default=None)
    changelog: list[Changelog] | None = field(default=None)
    cover_photo_url: str | None = field(default=None)
    id: str | None = field(default=None)
    last_sync_time: time | None = field(default=None)
    place: str | None = field(default=None)
    title: str | None = field(default=None)
