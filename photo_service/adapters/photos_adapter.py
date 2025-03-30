"""Module for photo adapter."""

from typing import Any

from .adapter import Adapter


class PhotosAdapter(Adapter):
    """Class representing an adapter for photos."""

    @classmethod
    async def create_photo(cls: Any, db: Any, photo: dict) -> str:  # pragma: no cover
        """Create photo function."""
        return await db.photos_collection.insert_one(photo)

    @classmethod
    async def get_all_photos(
        cls: Any, db: Any, event_id: str
    ) -> list:  # pragma: no cover
        """Get all photos function."""
        return await db.photos_collection.find(
            {"event_id": event_id}
        ).sort("time", -1)

    @classmethod
    async def get_photo_by_g_base_url(
        cls: Any, db: Any, g_base_url: str
    ) -> dict:  # pragma: no cover
        """Get photo function."""
        return await db.photos_collection.find_one({"g_base_url": g_base_url})

    @classmethod
    async def get_photo_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get photo function."""
        return await db.photos_collection.find_one({"g_id": g_id})

    @classmethod
    async def get_photo_by_id(cls: Any, db: Any, c_id: str) -> dict:  # pragma: no cover
        """Get photo function."""
        return await db.photos_collection.find_one({"id": c_id})

    @classmethod
    async def get_photos_by_race_id(
        cls: Any, db: Any, race_id: str
    ) -> list:  # pragma: no cover
        """Get all photos by race_id function."""
        return await db.photos_collection.find(
            {"race_id": race_id}
        ).sort("time", -1)

    @classmethod
    async def get_photos_by_raceclass(
        cls: Any, db: Any, event_id: str, raceclass: str
    ) -> list:  # pragma: no cover
        """Get all photos by raceclass function."""
        return await db.photos_collection.find(
            {"raceclass": raceclass, "event_id": event_id}
        ).sort("time", -1)

    @classmethod
    async def get_photos_starred_by_raceclass(
        cls: Any, db: Any, event_id: str, raceclass: str
    ) -> list:  # pragma: no cover
        """Get all photos by raceclass function."""
        return await db.photos_collection.find(
            {"starred": True, "raceclass": raceclass, "event_id": event_id}
        ).sort("time", -1)

    @classmethod
    async def get_photos_starred(
        cls: Any, db: Any, event_id: str
    ) -> list:  # pragma: no cover
        """Get all photos by raceclass function."""
        return await db.photos_collection.find(
            {"starred": True, "event_id": event_id}
        ).sort("time", -1)

    @classmethod
    async def update_photo(
        cls: Any, db: Any, c_id: str, photo: dict
    ) -> str | None:  # pragma: no cover
        """Get photo function."""
        return await db.photos_collection.replace_one({"id": c_id}, photo)

    @classmethod
    async def delete_photo(
        cls: Any, db: Any, c_id: str
    ) -> str | None:  # pragma: no cover
        """Get photo function."""
        return await db.photos_collection.delete_one({"id": c_id})
