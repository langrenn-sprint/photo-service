"""Module for photo adapter."""
from abc import ABC, abstractmethod
from typing import Any, List, Optional


class Adapter(ABC):
    """Class representing an adapter interface."""

    @classmethod
    @abstractmethod
    async def get_all_photos(cls: Any, db: Any) -> List:  # pragma: no cover
        """Get all photos function."""
        raise NotImplementedError() from None

    @classmethod
    @abstractmethod
    async def create_photo(cls: Any, db: Any, photo: dict) -> str:  # pragma: no cover
        """Create photo function."""
        raise NotImplementedError() from None

    @classmethod
    @abstractmethod
    async def get_photo_by_id(cls: Any, db: Any, id: str) -> dict:  # pragma: no cover
        """Get photo by id function."""
        raise NotImplementedError() from None

    @classmethod
    @abstractmethod
    async def update_photo(
        cls: Any, db: Any, id: str, photo: dict
    ) -> Optional[str]:  # pragma: no cover
        """Get photo function."""
        raise NotImplementedError() from None

    @classmethod
    @abstractmethod
    async def delete_photo(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get photo function."""
        raise NotImplementedError() from None
