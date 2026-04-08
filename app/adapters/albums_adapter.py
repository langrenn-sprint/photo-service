"""Module for albums adapter."""

import logging
from typing import Any


class AlbumsAdapter:
    """Class representing an adapter for albums."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def create_album(cls, album: dict) -> str:  # pragma: no cover
        """Create album function."""
        return await cls.database.albums_collection.insert_one(album)

    @classmethod
    async def get_all_albums(cls) -> list:  # pragma: no cover
        """Get all albums function."""
        cursor = cls.database.albums_collection.find()
        return await cursor.to_list(None)

    @classmethod
    async def get_album_by_g_id(cls, g_id: str) -> dict:  # pragma: no cover
        """Get album by g_id function."""
        return await cls.database.albums_collection.find_one({"g_id": g_id})

    @classmethod
    async def get_album_by_id(cls, c_id: str) -> dict:  # pragma: no cover
        """Get album by id function."""
        return await cls.database.albums_collection.find_one({"id": c_id})

    @classmethod
    async def update_album(cls, c_id: str, album: dict) -> str | None:  # pragma: no cover
        """Update album function."""
        return await cls.database.albums_collection.replace_one({"id": c_id}, album)

    @classmethod
    async def delete_album(cls, c_id: str) -> str | None:  # pragma: no cover
        """Delete album function."""
        return await cls.database.albums_collection.delete_one({"id": c_id})
