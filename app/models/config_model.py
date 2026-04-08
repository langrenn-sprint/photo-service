"""Config model module."""

from pydantic import BaseModel


class Config(BaseModel):
    """Model with details about a config entry."""

    event_id: str
    key: str
    value: str
    id: str | None = None
