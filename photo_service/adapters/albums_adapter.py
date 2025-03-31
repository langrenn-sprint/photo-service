"""Module for sync adapter."""

from typing import Any

from .adapter import Adapter


class AlbumsAdapter(Adapter):
    """Class representing an adapter for sync-ed albums."""

    @classmethod
    async def create_album(cls: Any, db: Any, album: dict) -> str:  # pragma: no cover
        """Create album function."""
        return await db.albums_collection.insert_one(album)

    @classmethod
    async def get_all_albums(cls: Any, db: Any) -> list:  # pragma: no cover
        """Get all albums function."""
        cursor = db.albums_collection.find()
        return await cursor.to_list(None)

    @classmethod
    async def get_album_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get album function."""
        return await db.albums_collection.find_one({"g_id": g_id})

    @classmethod
    async def get_album_by_id(cls: Any, db: Any, c_id: str) -> dict:  # pragma: no cover
        """Get album function."""
        return await db.albums_collection.find_one({"id": c_id})

    @classmethod
    async def update_album(
        cls: Any, db: Any, c_id: str, album: dict
    ) -> str | None:  # pragma: no cover
        """Get album function."""
        return await db.albums_collection.replace_one({"id": c_id}, album)

    @classmethod
    async def delete_album(
        cls: Any, db: Any, c_id: str
    ) -> str | None:  # pragma: no cover
        """Get album function."""
        return await db.albums_collection.delete_one({"id": c_id})
