"""Module for status adapter."""
from typing import Any, List, Optional

from .adapter import Adapter


class StatusAdapter(Adapter):
    """Class representing an adapter for sync-ed status."""

    @classmethod
    async def create_status(cls: Any, db: Any, status: dict) -> str:  # pragma: no cover
        """Create status function."""
        result = await db.status_collection.insert_one(status)
        return result

    @classmethod
    async def get_status(
        cls: Any, db: Any, event_id: str, status_type: str
    ) -> List:  # pragma: no cover
        """Get all status function."""
        status: List = []
        cursor = db.status_collection.find({"type": status_type, "event_id": event_id})
        for status in await cursor.to_list(None):
            status.append(status)
        return status

    @classmethod
    async def delete_status(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get status function."""
        result = await db.status_collection.delete_one({"id": id})
        return result
