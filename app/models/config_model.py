"""Config model module."""

from pydantic import BaseModel


class Config(BaseModel):
    """Model with details about a config entry."""

    event_id: str
    key: str
    value: str | int | float | bool | list | dict
    id: str | None = None
