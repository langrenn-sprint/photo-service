"""Changelog model module."""

from datetime import datetime

from pydantic import BaseModel


class Changelog(BaseModel):
    """Model representing a changelog entry."""

    timestamp: datetime
    user_id: str
    comment: str
