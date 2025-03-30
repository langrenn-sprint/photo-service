"""Module for ai events adapter."""

from typing import Any

from .adapter import Adapter


class VideoEventsAdapter(Adapter):
    """Class representing an adapter for video_events."""

    @classmethod
    async def create_video_event(
        cls: Any, db: Any, video_event: dict
    ) -> str:  # pragma: no cover
        """Create video_event function."""
        return await db.video_events_collection.insert_one(video_event)

    @classmethod
    async def get_all_video_events(
        cls: Any, db: Any, event_id: str
    ) -> list:  # pragma: no cover
        """Get all video_events function."""
        return await db.video_events_collection.find({"event_id": event_id}).to_list(None)

    @classmethod
    async def get_video_event_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get video_event function."""
        return await db.video_events_collection.find_one({"g_id": g_id})

    @classmethod
    async def get_video_event_by_id(
        cls: Any, db: Any, c_id: str
    ) -> dict:  # pragma: no cover
        """Get video_event function."""
        return await db.video_events_collection.find_one({"id": c_id})

    @classmethod
    async def update_video_event(
        cls: Any, db: Any, c_id: str, video_event: dict
    ) -> str | None:  # pragma: no cover
        """Get video_event function."""
        return await db.video_events_collection.replace_one({"id": c_id}, video_event)

    @classmethod
    async def delete_video_event(
        cls: Any, db: Any, c_id: str
    ) -> str | None:  # pragma: no cover
        """Get video_event function."""
        return await db.video_events_collection.delete_one({"id": c_id})
