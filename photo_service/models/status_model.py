"""Photo data class module."""

from dataclasses import dataclass, field
from datetime import time

from dataclasses_json import DataClassJsonMixin


@dataclass
class Status(DataClassJsonMixin):
    """Data class with details about a sync-ed config."""

    event_id: str
    time: time
    type: str
    message: str
    id: str | None = field(default=None)
