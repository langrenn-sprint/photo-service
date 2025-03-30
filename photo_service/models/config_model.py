"""Photo data class module."""

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin


@dataclass
class Config(DataClassJsonMixin):
    """Data class with details about a sync-ed config."""

    event_id: str
    key: str
    value: str
    id: str | None = field(default=None)
