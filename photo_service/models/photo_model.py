"""Photo data class module."""

from dataclasses import dataclass, field
from datetime import time

from dataclasses_json import DataClassJsonMixin


@dataclass
class Photo(DataClassJsonMixin):
    """Data class with details about a photo."""

    name: str
    is_photo_finish: bool = False
    is_start_registration: bool = False
    starred: bool = False
    confidence: int = 0
    event_id: str | None = field(default=None)
    creation_time: time | None = field(default=None)
    information: dict | None = field(default=None)
    id: str | None = field(default=None)
    race_id: str | None = field(default=None)
    raceclass: str | None = field(default=None)
    biblist: list[int] | None = field(default=None)
    clublist: list[str] | None = field(default=None)
    g_id: str | None = field(default=None)
    g_product_url: str | None = field(default=None)
    g_base_url: str | None = field(default=None)
    ai_information: dict | None = field(default=None)
