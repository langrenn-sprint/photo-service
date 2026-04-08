"""Status model module."""

from pydantic import BaseModel


class Status(BaseModel):
    """Model with details about a status entry."""

    event_id: str
    time: str
    type: str
    message: str
    details: dict | None = None
    id: str | None = None
