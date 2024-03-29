"""Module for photo adapter."""
from typing import Any, List, Optional

from .adapter import Adapter


class PhotosAdapter(Adapter):
    """Class representing an adapter for photos."""

    @classmethod
    async def create_photo(cls: Any, db: Any, photo: dict) -> str:  # pragma: no cover
        """Create photo function."""
        result = await db.photos_collection.insert_one(photo)
        return result

    @classmethod
    async def get_all_photos(cls: Any, db: Any) -> List:  # pragma: no cover
        """Get all photos function."""
        photos: List = []
        cursor = db.photos_collection.find()
        for photo in await cursor.to_list(None):
            photos.append(photo)
        return photos

    @classmethod
    async def get_photo_by_g_base_url(
        cls: Any, db: Any, g_base_url: str
    ) -> dict:  # pragma: no cover
        """Get photo function."""
        result = await db.photos_collection.find_one({"g_base_url": g_base_url})
        return result

    @classmethod
    async def get_photo_by_g_id(
        cls: Any, db: Any, g_id: str
    ) -> dict:  # pragma: no cover
        """Get photo function."""
        result = await db.photos_collection.find_one({"g_id": g_id})
        return result

    @classmethod
    async def get_photo_by_id(cls: Any, db: Any, id: str) -> dict:  # pragma: no cover
        """Get photo function."""
        result = await db.photos_collection.find_one({"id": id})
        return result

    @classmethod
    async def get_photos_by_raceclass(
        cls: Any, db: Any, raceclass: str
    ) -> List:  # pragma: no cover
        """Get all photos by raceclass function."""
        photos: List = []
        cursor = db.photos_collection.find({"raceclass": raceclass})
        for photo in await cursor.to_list(None):
            photos.append(photo)
        return photos

    @classmethod
    async def get_photos_starred_by_raceclass(
        cls: Any, db: Any, raceclass: str
    ) -> List:  # pragma: no cover
        """Get all photos by raceclass function."""
        photos: List = []
        cursor = db.photos_collection.find({"starred": True, "raceclass": raceclass})
        for photo in await cursor.to_list(None):
            photos.append(photo)
        return photos

    @classmethod
    async def get_photos_starred(cls: Any, db: Any) -> List:  # pragma: no cover
        """Get all photos by raceclass function."""
        photos: List = []
        cursor = db.photos_collection.find({"starred": True})
        for photo in await cursor.to_list(None):
            photos.append(photo)
        return photos

    @classmethod
    async def update_photo(
        cls: Any, db: Any, id: str, photo: dict
    ) -> Optional[str]:  # pragma: no cover
        """Get photo function."""
        result = await db.photos_collection.replace_one({"id": id}, photo)
        return result

    @classmethod
    async def delete_photo(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get photo function."""
        result = await db.photos_collection.delete_one({"id": id})
        return result
