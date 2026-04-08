"""VideoEvent model module."""

from pydantic import BaseModel


class VideoEvent(BaseModel):
    """Model with details about a video event."""

    event_id: str
    id: str
    queue_name: str
    events: list[dict] | None = None
    sourceinfo: dict | None = None
    detections: list[dict] | None = None
    schemaversion: str | None = None
