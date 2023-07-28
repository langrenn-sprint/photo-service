"""Photo data class module."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class VideoEvent(DataClassJsonMixin):
    """Data class with details about a sync-ed video_event."""

    event_id: str
    id: str
    queue_name: str
    events: Optional[List[Dict]] = field(default=None)
    sourceInfo: Optional[Dict] = field(default=None)
    detections: Optional[List[Dict]] = field(default=None)
    schemaVersion: Optional[str] = field(default=None)
