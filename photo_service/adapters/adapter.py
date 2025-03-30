"""Module for photo adapter."""

from abc import ABC, abstractmethod
from typing import Any


class Adapter(ABC):
    """Class representing an adapter interface."""

    @classmethod
    @abstractmethod
    async def get_all_photos(
        cls: Any, db: Any, event_id: str
    ) -> list:  # pragma: no cover
        """Get all photos function."""
        raise NotImplementedError from None

    @classmethod
    @abstractmethod
    async def create_photo(cls: Any, db: Any, photo: dict) -> str:  # pragma: no cover
        """Create photo function."""
        raise NotImplementedError from None

    @classmethod
    @abstractmethod
    async def get_photo_by_id(cls: Any, db: Any, c_id: str) -> dict:  # pragma: no cover
        """Get photo by id function."""
        raise NotImplementedError from None

    @classmethod
    @abstractmethod
    async def update_photo(
        cls: Any, db: Any, c_id: str, photo: dict
    ) -> str | None:  # pragma: no cover
        """Update photo function."""
        raise NotImplementedError from None

    @classmethod
    @abstractmethod
    async def delete_photo(
        cls: Any, db: Any, c_id: str
    ) -> str | None:  # pragma: no cover
        """Get photo function."""
        raise NotImplementedError from None
