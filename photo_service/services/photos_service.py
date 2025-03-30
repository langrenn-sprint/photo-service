"""Module for photos service."""

import logging
import uuid
from typing import Any

from photo_service.adapters import PhotosAdapter
from photo_service.models import Photo

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create an uuid."""
    return str(uuid.uuid4())


class PhotoNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class PhotosService:
    """Class representing a service for photos."""

    @classmethod
    async def get_all_photos(cls: Any, db: Any, event_id: str) -> list[Photo]:
        """Get all photos function."""
        _photos = await PhotosAdapter.get_all_photos(db, event_id)
        photos = [Photo.from_dict(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_by_race_id(cls: Any, db: Any, race_id: str) -> list[Photo]:
        """Get all photos for one race function."""
        _photos = await PhotosAdapter.get_photos_by_race_id(db, race_id)
        photos = [Photo.from_dict(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_by_raceclass(
        cls: Any, db: Any, event_id: str, raceclass: str
    ) -> list[Photo]:
        """Get all photos for one raceclass function."""
        _photos = await PhotosAdapter.get_photos_by_raceclass(db, event_id, raceclass)
        photos = [Photo.from_dict(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_starred(cls: Any, db: Any, event_id: str) -> list[Photo]:
        """Get all photos by raceclass function."""
        _photos = await PhotosAdapter.get_photos_starred(db, event_id)
        photos = [Photo.from_dict(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_starred_by_raceclass(
        cls: Any, db: Any, event_id: str, raceclass: str
    ) -> list[Photo]:
        """Get all photos by raceclass function."""
        _photos = await PhotosAdapter.get_photos_starred_by_raceclass(
            db, event_id, raceclass
        )
        photos = [Photo.from_dict(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def create_photo(cls: Any, db: Any, photo: Photo) -> str | None:
        """Create photo function.

        Args:
            db (Any): the db
            photo (Photo): a photo instanse to be created

        Returns:
            Optional[str]: The id of the created photo. None otherwise.

        Raises:
            IllegalValueError: input object has illegal values

        """
        # Validation:
        if photo.id:
            err_msg = "Cannot create photo with input id."
            raise IllegalValueError(err_msg) from None
        # create id
        c_id = create_id()
        photo.id = c_id
        # insert new photo
        new_photo = photo.to_dict()
        result = await PhotosAdapter.create_photo(db, new_photo)
        logging.debug(f"inserted photo with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_photo_by_g_id(cls: Any, db: Any, g_id: str) -> Photo:
        """Get photo function."""
        photo = await PhotosAdapter.get_photo_by_g_id(db, g_id)
        # return the document if found:
        if photo:
            return Photo.from_dict(photo)
        err_msg = f"Photo with id {g_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def get_photo_by_g_base_url(cls: Any, db: Any, g_base_url: str) -> Photo:
        """Get photo function."""
        photo = await PhotosAdapter.get_photo_by_g_base_url(db, g_base_url)
        # return the document if found:
        if photo:
            return Photo.from_dict(photo)
        informasjon = f"Photo with g_base_url {g_base_url} not found"
        raise PhotoNotFoundError(informasjon) from None

    @classmethod
    async def get_photo_by_id(cls: Any, db: Any, c_id: str) -> Photo:
        """Get photo function."""
        photo = await PhotosAdapter.get_photo_by_id(db, c_id)
        # return the document if found:
        if photo:
            return Photo.from_dict(photo)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def update_photo(cls: Any, db: Any, c_id: str, photo: Photo) -> str | None:
        """Get photo function."""
        # get old document
        old_photo = await PhotosAdapter.get_photo_by_id(db, c_id)
        # update the photo if found:
        if old_photo:
            if photo.id != old_photo["id"]:
                err_msg = "Cannot change id for photo."
                raise IllegalValueError(err_msg) from None
            new_photo = photo.to_dict()
            return await PhotosAdapter.update_photo(db, c_id, new_photo)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def delete_photo(cls: Any, db: Any, c_id: str) -> str | None:
        """Get photo function."""
        # get old document
        photo = await PhotosAdapter.get_photo_by_id(db, c_id)
        # delete the document if found:
        if photo:
            return await PhotosAdapter.delete_photo(db, c_id)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None
