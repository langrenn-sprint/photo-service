"""Photo data class module."""
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class Photo(DataClassJsonMixin):
    """Data class with details about a photo."""

    name: str
    date_of_photo: Optional[date] = field(default=None)
    time_of_photo: Optional[time] = field(default=None)
    organiser: Optional[str] = field(default=None)
    webpage: Optional[str] = field(default=None)
    information: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
