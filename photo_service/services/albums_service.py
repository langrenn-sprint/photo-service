"""Module for albums service."""

import logging
import uuid
from typing import Any

from photo_service.adapters import AlbumsAdapter
from photo_service.models import Album

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create an uuid."""
    return str(uuid.uuid4())


class AlbumNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class AlbumsService:
    """Class representing a service for albums."""

    @classmethod
    async def get_all_albums(cls: Any, db: Any) -> list[Album]:
        """Get all albums function."""
        _albums = await AlbumsAdapter.get_all_albums(db)
        return [Album.from_dict(e) for e in _albums]

    @classmethod
    async def create_album(cls: Any, db: Any, album: Album) -> str | None:
        """Create album function.

        Args:
            db (Any): the db
            album (Album): a album instanse to be created

        Returns:
            Optional[str]: The id of the created album. None otherwise.

        Raises:
            IllegalValueError: input object has illegal values

        """
        # Validation:
        if album.id:
            err_msg = "Cannot create album with input id."
            raise IllegalValueError(err_msg) from None
        # create id
        a_id = create_id()
        album.id = a_id
        # insert new album
        new_album = album.to_dict()
        result = await AlbumsAdapter.create_album(db, new_album)
        logging.debug(f"inserted album with id: {a_id}")
        if result:
            return a_id
        return None

    @classmethod
    async def get_album_by_g_id(cls: Any, db: Any, g_id: str) -> Album:
        """Get album function."""
        album = await AlbumsAdapter.get_album_by_g_id(db, g_id)
        # return the document if found:
        if album:
            return Album.from_dict(album)
        err_msg = f"Album with id {g_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def get_album_by_id(cls: Any, db: Any, a_id: str) -> Album:
        """Get album function."""
        album = await AlbumsAdapter.get_album_by_id(db, a_id)
        # return the document if found:
        if album:
            return Album.from_dict(album)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def update_album(cls: Any, db: Any, a_id: str, album: Album) -> str | None:
        """Get album function."""
        # get old document
        old_album = await AlbumsAdapter.get_album_by_id(db, a_id)
        # update the album if found:
        if old_album:
            if album.id != old_album["id"]:
                err_msg = "Cannot change id for album."
                raise IllegalValueError(err_msg) from None
            new_album = album.to_dict()
            return await AlbumsAdapter.update_album(db, a_id, new_album)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def delete_album(cls: Any, db: Any, a_id: str) -> str | None:
        """Get album function."""
        # get old document
        album = await AlbumsAdapter.get_album_by_id(db, a_id)
        # delete the document if found:
        if album:
            return await AlbumsAdapter.delete_album(db, a_id)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None
