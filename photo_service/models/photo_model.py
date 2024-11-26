"""Photo data class module."""

from dataclasses import dataclass, field
from datetime import time
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class Photo(DataClassJsonMixin):
    """Data class with details about a photo."""

    name: str
    is_photo_finish: bool = False
    is_start_registration: bool = False
    starred: bool = False
    confidence: int = 0
    event_id: Optional[str] = field(default=None)
    creation_time: Optional[time] = field(default=None)
    information: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
    race_id: Optional[str] = field(default=None)
    raceclass: Optional[str] = field(default=None)
    biblist: Optional[List[int]] = field(default=None)
    clublist: Optional[List[str]] = field(default=None)
    g_id: Optional[str] = field(default=None)
    g_product_url: Optional[str] = field(default=None)
    g_base_url: Optional[str] = field(default=None)
    ai_information: Optional[Dict] = field(default=None)
