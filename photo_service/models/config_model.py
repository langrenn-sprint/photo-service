"""Photo data class module."""
from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class Config(DataClassJsonMixin):
    """Data class with details about a sync-ed config."""

    event_id: str
    key: str
    value: str
    id: Optional[str] = field(default=None)
