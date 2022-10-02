"""Photo data class module."""
from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin

from .changelog import Changelog


@dataclass
class Album(DataClassJsonMixin):
    """Data class with details about a sync-ed album."""

    g_id: str
    is_photo_finish: bool = False
    sync_on: bool = False
    event_id: Optional[str] = field(default=None)
    camera_position: Optional[str] = field(default=None)
    changelog: Optional[List[Changelog]] = field(default=None)
    cover_photo_url: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
    last_sync_time: Optional[time] = field(default=None)
    place: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
