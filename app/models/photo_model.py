"""Photo model module."""

from pydantic import BaseModel


class Photo(BaseModel):
    """Model with details about a photo."""

    name: str
    is_photo_finish: bool = False
    is_start_registration: bool = False
    starred: bool = False
    confidence: int = 0
    event_id: str | None = None
    creation_time: str | None = None
    information: dict | None = None
    id: str | None = None
    race_id: str | None = None
    raceclass: str | None = None
    biblist: list[int] | None = None
    clublist: list[str] | None = None
    g_id: str | None = None
    g_product_url: str | None = None
    g_base_url: str | None = None
    ai_information: dict | None = None
