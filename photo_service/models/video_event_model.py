"""Photo data class module."""

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin


@dataclass
class VideoEvent(DataClassJsonMixin):
    """Data class with details about a sync-ed video_event."""

    event_id: str
    id: str
    queue_name: str
    events: list[dict] | None = field(default=None)
    sourceinfo: dict | None = field(default=None)
    detections: list[dict] | None = field(default=None)
    schemaversion: str | None = field(default=None)
