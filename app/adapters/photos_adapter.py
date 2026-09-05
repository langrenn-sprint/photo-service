"""Module for photos adapter."""

import logging
from typing import Any


class PhotosAdapter:
    """Class representing an adapter for photos."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def create_photo(cls, photo: dict) -> str:  # pragma: no cover
        """Create photo function."""
        return await cls.database.photos_collection.insert_one(photo)

    @classmethod
    async def get_all_photos(cls, event_id: str) -> list:  # pragma: no cover
        """Get all photos function."""
        cursor = cls.database.photos_collection.find({"event_id": event_id}).sort(
            "time", -1
        )
        return await cursor.to_list(None)

    @classmethod
    async def get_photo_by_g_base_url(cls, g_base_url: str) -> dict:  # pragma: no cover
        """Get photo by g_base_url function."""
        return await cls.database.photos_collection.find_one({"g_base_url": g_base_url})

    @classmethod
    async def get_photo_by_g_id(cls, g_id: str) -> dict:  # pragma: no cover
        """Get photo by g_id function."""
        return await cls.database.photos_collection.find_one({"g_id": g_id})

    @classmethod
    async def get_photo_by_id(cls, c_id: str) -> dict:  # pragma: no cover
        """Get photo by id function."""
        return await cls.database.photos_collection.find_one({"id": c_id})

    @classmethod
    async def get_photos_by_race_id(cls, race_id: str) -> list:  # pragma: no cover
        """Get all photos by race_id function."""
        cursor = cls.database.photos_collection.find({"race_id": race_id}).sort(
            "time", -1
        )
        return await cursor.to_list(None)

    @classmethod
    async def get_photos_by_raceclass(
        cls, event_id: str, raceclass: str
    ) -> list:  # pragma: no cover
        """Get all photos by raceclass function."""
        cursor = cls.database.photos_collection.find(
            {"raceclass": raceclass, "event_id": event_id}
        ).sort("time", -1)
        return await cursor.to_list(None)

    @classmethod
    async def get_photos_starred_by_raceclass(
        cls, event_id: str, raceclass: str
    ) -> list:  # pragma: no cover
        """Get all starred photos by raceclass function."""
        cursor = cls.database.photos_collection.find(
            {"starred": True, "raceclass": raceclass, "event_id": event_id}
        ).sort("time", -1)
        return await cursor.to_list(None)

    @classmethod
    async def get_photos_starred(cls, event_id: str) -> list:  # pragma: no cover
        """Get all starred photos function."""
        cursor = cls.database.photos_collection.find(
            {"starred": True, "event_id": event_id}
        ).sort("time", -1)
        return await cursor.to_list(None)

    @classmethod
    async def update_photo(
        cls, c_id: str, photo: dict
    ) -> str | None:  # pragma: no cover
        """Update photo function."""
        return await cls.database.photos_collection.replace_one({"id": c_id}, photo)

    @classmethod
    async def delete_photo(cls, c_id: str) -> str | None:  # pragma: no cover
        """Delete photo function."""
        return await cls.database.photos_collection.delete_one({"id": c_id})
