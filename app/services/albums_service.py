"""Module for albums service."""

import logging
import uuid

from app.adapters import AlbumsAdapter
from app.models import Album

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create a uuid."""
    return str(uuid.uuid4())


class AlbumNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class AlbumsService:
    """Class representing a service for albums."""

    @classmethod
    async def get_all_albums(cls) -> list[Album]:
        """Get all albums function."""
        _albums = await AlbumsAdapter.get_all_albums()
        return [Album.model_validate(e) for e in _albums]

    @classmethod
    async def create_album(cls, album: Album) -> str | None:
        """Create album function."""
        if album.id:
            err_msg = "Cannot create album with input id."
            raise IllegalValueError(err_msg) from None
        a_id = create_id()
        album.id = a_id
        new_album = album.model_dump()
        result = await AlbumsAdapter.create_album(new_album)
        logging.debug(f"inserted album with id: {a_id}")
        if result:
            return a_id
        return None

    @classmethod
    async def get_album_by_g_id(cls, g_id: str) -> Album:
        """Get album by g_id function."""
        album = await AlbumsAdapter.get_album_by_g_id(g_id)
        if album:
            return Album.model_validate(album)
        err_msg = f"Album with id {g_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def get_album_by_id(cls, a_id: str) -> Album:
        """Get album by id function."""
        album = await AlbumsAdapter.get_album_by_id(a_id)
        if album:
            return Album.model_validate(album)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def update_album(cls, a_id: str, album: Album) -> str | None:
        """Update album function."""
        old_album = await AlbumsAdapter.get_album_by_id(a_id)
        if old_album:
            if album.id != old_album["id"]:
                err_msg = "Cannot change id for album."
                raise IllegalValueError(err_msg) from None
            new_album = album.model_dump()
            return await AlbumsAdapter.update_album(a_id, new_album)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None

    @classmethod
    async def delete_album(cls, a_id: str) -> str | None:
        """Delete album function."""
        album = await AlbumsAdapter.get_album_by_id(a_id)
        if album:
            return await AlbumsAdapter.delete_album(a_id)
        err_msg = f"Album with id {a_id} not found"
        raise AlbumNotFoundError(err_msg) from None
