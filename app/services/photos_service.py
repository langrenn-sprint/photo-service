"""Module for photos service."""

import logging
import uuid

from app.adapters import PhotosAdapter
from app.models import Photo

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create a uuid."""
    return str(uuid.uuid4())


class PhotoNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class PhotosService:
    """Class representing a service for photos."""

    @classmethod
    async def get_all_photos(cls, event_id: str) -> list[Photo]:
        """Get all photos function."""
        _photos = await PhotosAdapter.get_all_photos(event_id)
        photos = [Photo.model_validate(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_by_race_id(cls, race_id: str) -> list[Photo]:
        """Get all photos for one race function."""
        _photos = await PhotosAdapter.get_photos_by_race_id(race_id)
        photos = [Photo.model_validate(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_by_raceclass(cls, event_id: str, raceclass: str) -> list[Photo]:
        """Get all photos for one raceclass function."""
        _photos = await PhotosAdapter.get_photos_by_raceclass(event_id, raceclass)
        photos = [Photo.model_validate(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_starred(cls, event_id: str) -> list[Photo]:
        """Get all starred photos function."""
        _photos = await PhotosAdapter.get_photos_starred(event_id)
        photos = [Photo.model_validate(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def get_photos_starred_by_raceclass(cls, event_id: str, raceclass: str) -> list[Photo]:
        """Get all starred photos by raceclass function."""
        _photos = await PhotosAdapter.get_photos_starred_by_raceclass(event_id, raceclass)
        photos = [Photo.model_validate(e) for e in _photos]
        return sorted(
            photos,
            key=lambda k: (
                k.creation_time is not None,
                k.creation_time,
            ),
        )

    @classmethod
    async def create_photo(cls, photo: Photo) -> str | None:
        """Create photo function."""
        if photo.id:
            err_msg = "Cannot create photo with input id."
            raise IllegalValueError(err_msg) from None
        c_id = create_id()
        photo.id = c_id
        new_photo = photo.model_dump()
        result = await PhotosAdapter.create_photo(new_photo)
        logging.debug(f"inserted photo with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_photo_by_g_id(cls, g_id: str) -> Photo:
        """Get photo by g_id function."""
        photo = await PhotosAdapter.get_photo_by_g_id(g_id)
        if photo:
            return Photo.model_validate(photo)
        err_msg = f"Photo with id {g_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def get_photo_by_g_base_url(cls, g_base_url: str) -> Photo:
        """Get photo by g_base_url function."""
        photo = await PhotosAdapter.get_photo_by_g_base_url(g_base_url)
        if photo:
            return Photo.model_validate(photo)
        informasjon = f"Photo with g_base_url {g_base_url} not found"
        raise PhotoNotFoundError(informasjon) from None

    @classmethod
    async def get_photo_by_id(cls, c_id: str) -> Photo:
        """Get photo by id function."""
        photo = await PhotosAdapter.get_photo_by_id(c_id)
        if photo:
            return Photo.model_validate(photo)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def update_photo(cls, c_id: str, photo: Photo) -> str | None:
        """Update photo function."""
        old_photo = await PhotosAdapter.get_photo_by_id(c_id)
        if old_photo:
            if photo.id != old_photo["id"]:
                err_msg = "Cannot change id for photo."
                raise IllegalValueError(err_msg) from None
            new_photo = photo.model_dump()
            return await PhotosAdapter.update_photo(c_id, new_photo)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None

    @classmethod
    async def delete_photo(cls, c_id: str) -> str | None:
        """Delete photo function."""
        photo = await PhotosAdapter.get_photo_by_id(c_id)
        if photo:
            return await PhotosAdapter.delete_photo(c_id)
        err_msg = f"Photo with id {c_id} not found."
        raise PhotoNotFoundError(err_msg) from None
