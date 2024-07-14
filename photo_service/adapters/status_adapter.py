"""Module for status adapter."""
import logging
from typing import Any, List, Optional

from .adapter import Adapter


class StatusNotFoundException(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class StatusAdapter(Adapter):
    """Class representing an adapter for status messages."""

    @classmethod
    async def create_status(cls: Any, db: Any, status: dict) -> str:  # pragma: no cover
        """Create status function."""
        result = await db.status_collection.insert_one(status)
        return result

    @classmethod
    async def get_status_by_id(cls: Any, db: Any, id: str) -> dict:  # pragma: no cover
        """Get status function."""
        result = await db.status_collection.find_one({"id": id})
        return result

    @classmethod
    async def get_all_status(
        cls: Any, db: Any, event_id: str, count: int
    ) -> List[dict]:  # pragma: no cover
        """Get latest status function."""
        statuses: List = []
        try:
            cursor = (
                db.status_collection.find({"event_id": event_id})
                .sort("time", -1)
                .limit(count)
            )
            for status in await cursor.to_list(None):
                statuses.append(status)
        except Exception as e:
            logging.error(e)
        return statuses

    @classmethod
    async def get_all_status_by_type(
        cls: Any, db: Any, event_id: str, status_type: str, count: int
    ) -> List[dict]:  # pragma: no cover
        """Get latest status function."""
        statuses: List = []
        try:
            cursor = (
                db.status_collection.find({"type": status_type, "event_id": event_id})
                .sort("time", -1)
                .limit(count)
            )
            for status in await cursor.to_list(None):
                statuses.append(status)
        except Exception as e:
            logging.error(e)
        return statuses

    @classmethod
    async def delete_status(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get status function."""
        result = await db.status_collection.delete_one({"id": id})
        return result
