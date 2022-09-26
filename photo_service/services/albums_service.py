"""Module for albums service."""
import logging
from typing import Any, List, Optional
import uuid

from photo_service.adapters import AlbumsAdapter
from photo_service.models import Album
from .exceptions import IllegalValueException


def create_id() -> str:  # pragma: no cover
    """Creates an uuid."""
    return str(uuid.uuid4())


class AlbumNotFoundException(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class AlbumsService:
    """Class representing a service for albums."""

    @classmethod
    async def get_all_albums(cls: Any, db: Any) -> List[Album]:
        """Get all albums function."""
        albums: List[Album] = []
        _albums = await AlbumsAdapter.get_all_albums(db)
        for e in _albums:
            albums.append(Album.from_dict(e))
        return albums

    @classmethod
    async def create_album(cls: Any, db: Any, album: Album) -> Optional[str]:
        """Create album function.

        Args:
            db (Any): the db
            album (Album): a album instanse to be created

        Returns:
            Optional[str]: The id of the created album. None otherwise.

        Raises:
            IllegalValueException: input object has illegal values
        """
        # Validation:
        if album.id:
            raise IllegalValueException("Cannot create album with input id.") from None
        # create id
        id = create_id()
        album.id = id
        # insert new album
        new_album = album.to_dict()
        result = await AlbumsAdapter.create_album(db, new_album)
        logging.debug(f"inserted album with id: {id}")
        if result:
            return id
        return None

    @classmethod
    async def get_album_by_g_id(cls: Any, db: Any, g_id: str) -> Album:
        """Get album function."""
        album = await AlbumsAdapter.get_album_by_g_id(db, g_id)
        # return the document if found:
        if album:
            return Album.from_dict(album)
        raise AlbumNotFoundException(f"Album with g_id {g_id} not found") from None

    @classmethod
    async def get_album_by_id(cls: Any, db: Any, id: str) -> Album:
        """Get album function."""
        album = await AlbumsAdapter.get_album_by_id(db, id)
        # return the document if found:
        if album:
            return Album.from_dict(album)
        raise AlbumNotFoundException(f"Album with id {id} not found") from None

    @classmethod
    async def update_album(cls: Any, db: Any, id: str, album: Album) -> Optional[str]:
        """Get album function."""
        # get old document
        old_album = await AlbumsAdapter.get_album_by_id(db, id)
        # update the album if found:
        if old_album:
            if album.id != old_album["id"]:
                raise IllegalValueException("Cannot change id for album.") from None
            new_album = album.to_dict()
            result = await AlbumsAdapter.update_album(db, id, new_album)
            return result
        raise AlbumNotFoundException(f"Album with id {id} not found.") from None

    @classmethod
    async def delete_album(cls: Any, db: Any, id: str) -> Optional[str]:
        """Get album function."""
        # get old document
        album = await AlbumsAdapter.get_album_by_id(db, id)
        # delete the document if found:
        if album:
            result = await AlbumsAdapter.delete_album(db, id)
            return result
        raise AlbumNotFoundException(f"Album with id {id} not found") from None
