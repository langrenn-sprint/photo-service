"""Module for ai events adapter."""

from typing import Any, List, Optional

from .adapter import Adapter


class VideoEventsAdapter(Adapter):
    """Class representing an adapter for video_events."""

    @classmethod
    async def create_video_event(
        cls: Any, db: Any, video_event: dict
    ) -> str:  # pragma: no cover
        """Create video_event function."""
        result = await db.video_events_collection.insert_one(video_event)
        return result

    @classmethod
    async def get_all_video_events(
        cls: Any, db: Any, event_id: str
    ) -> List:  # pragma: no cover
        """Get all video_events function."""
        video_events: List = []
        cursor = db.video_events_collection.find({"event_id": event_id})
        for video_event in await cursor.to_list(None):
            video_events.append(video_event)
        return video_events

    @classmethod
    async def get_video_event_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get video_event function."""
        result = await db.video_events_collection.find_one({"g_id": g_id})
        return result

    @classmethod
    async def get_video_event_by_id(
        cls: Any, db: Any, id: str
    ) -> dict:  # pragma: no cover
        """Get video_event function."""
        result = await db.video_events_collection.find_one({"id": id})
        return result

    @classmethod
    async def update_video_event(
        cls: Any, db: Any, id: str, video_event: dict
    ) -> Optional[str]:  # pragma: no cover
        """Get video_event function."""
        result = await db.video_events_collection.replace_one({"id": id}, video_event)
        return result

    @classmethod
    async def delete_video_event(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get video_event function."""
        result = await db.video_events_collection.delete_one({"id": id})
        return result
