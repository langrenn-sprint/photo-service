"""Module for sync adapter."""

from typing import Any, List, Optional

from .adapter import Adapter


class AlbumsAdapter(Adapter):
    """Class representing an adapter for sync-ed albums."""

    @classmethod
    async def create_album(cls: Any, db: Any, album: dict) -> str:  # pragma: no cover
        """Create album function."""
        result = await db.albums_collection.insert_one(album)
        return result

    @classmethod
    async def get_all_albums(cls: Any, db: Any) -> List:  # pragma: no cover
        """Get all albums function."""
        albums: List = []
        cursor = db.albums_collection.find()
        for album in await cursor.to_list(None):
            albums.append(album)
        return albums

    @classmethod
    async def get_album_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get album function."""
        result = await db.albums_collection.find_one({"g_id": g_id})
        return result

    @classmethod
    async def get_album_by_id(cls: Any, db: Any, id: str) -> dict:  # pragma: no cover
        """Get album function."""
        result = await db.albums_collection.find_one({"id": id})
        return result

    @classmethod
    async def update_album(
        cls: Any, db: Any, id: str, album: dict
    ) -> Optional[str]:  # pragma: no cover
        """Get album function."""
        result = await db.albums_collection.replace_one({"id": id}, album)
        return result

    @classmethod
    async def delete_album(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get album function."""
        result = await db.albums_collection.delete_one({"id": id})
        return result
