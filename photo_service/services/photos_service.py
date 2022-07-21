"""Module for photos service."""
import logging
from typing import Any, List, Optional
import uuid

from photo_service.adapters import PhotosAdapter
from photo_service.models import Photo
from .exceptions import IllegalValueException


def create_id() -> str:  # pragma: no cover
    """Creates an uuid."""
    return str(uuid.uuid4())


class PhotoNotFoundException(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class PhotosService:
    """Class representing a service for photos."""

    @classmethod
    async def get_all_photos(cls: Any, db: Any) -> List[Photo]:
        """Get all photos function."""
        photos: List[Photo] = []
        _photos = await PhotosAdapter.get_all_photos(db)
        for e in _photos:
            photos.append(Photo.from_dict(e))
        _s = sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
            reverse=True,
        )
        return _s

    @classmethod
    async def create_photo(cls: Any, db: Any, photo: Photo) -> Optional[str]:
        """Create photo function.

        Args:
            db (Any): the db
            photo (Photo): a photo instanse to be created

        Returns:
            Optional[str]: The id of the created photo. None otherwise.

        Raises:
            IllegalValueException: input object has illegal values
        """
        # Validation:
        if photo.id:
            raise IllegalValueException("Cannot create photo with input id.") from None
        # create id
        id = create_id()
        photo.id = id
        # insert new photo
        new_photo = photo.to_dict()
        result = await PhotosAdapter.create_photo(db, new_photo)
        logging.debug(f"inserted photo with id: {id}")
        if result:
            return id
        return None

    @classmethod
    async def get_photo_by_g_id(cls: Any, db: Any, g_id: str) -> Photo:
        """Get photo function."""
        photo = await PhotosAdapter.get_photo_by_g_id(db, g_id)
        # return the document if found:
        if photo:
            return Photo.from_dict(photo)
        raise PhotoNotFoundException(f"Photo with g_id {g_id} not found") from None

    @classmethod
    async def get_photo_by_id(cls: Any, db: Any, id: str) -> Photo:
        """Get photo function."""
        photo = await PhotosAdapter.get_photo_by_id(db, id)
        # return the document if found:
        if photo:
            return Photo.from_dict(photo)
        raise PhotoNotFoundException(f"Photo with id {id} not found") from None

    @classmethod
    async def update_photo(cls: Any, db: Any, id: str, photo: Photo) -> Optional[str]:
        """Get photo function."""
        # get old document
        old_photo = await PhotosAdapter.get_photo_by_id(db, id)
        # update the photo if found:
        if old_photo:
            if photo.id != old_photo["id"]:
                raise IllegalValueException("Cannot change id for photo.") from None
            new_photo = photo.to_dict()
            result = await PhotosAdapter.update_photo(db, id, new_photo)
            return result
        raise PhotoNotFoundException(f"Photo with id {id} not found.") from None

    @classmethod
    async def delete_photo(cls: Any, db: Any, id: str) -> Optional[str]:
        """Get photo function."""
        # get old document
        photo = await PhotosAdapter.get_photo_by_id(db, id)
        # delete the document if found:
        if photo:
            result = await PhotosAdapter.delete_photo(db, id)
            return result
        raise PhotoNotFoundException(f"Photo with id {id} not found") from None
