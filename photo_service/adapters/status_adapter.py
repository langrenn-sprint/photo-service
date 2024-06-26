"""Module for status adapter."""
from typing import Any, List, Optional
import uuid

from .adapter import Adapter


def create_id() -> str:  # pragma: no cover
    """Creates an uuid."""
    return str(uuid.uuid4())


class StatusAdapter(Adapter):
    """Class representing an adapter for status messages."""

    @classmethod
    async def create_status(
        cls: Any, db: Any, status: dict
    ) -> Optional[str]:  # pragma: no cover
        """Create status function."""
        # Validation:
        if "id" in status.keys():
            raise Exception("Cannot create status with input id.") from None
        # create id and insert
        status["id"] = create_id()
        result = await db.status_collection.insert_one(status)
        if result:
            return status["id"]
        return None

    @classmethod
    async def get_status(
        cls: Any, db: Any, event_id: str, count: int
    ) -> List[dict]:  # pragma: no cover
        """Get latest status function."""
        statuses: List = []
        cursor = (
            db.status_collection.find({"event_id": event_id})
            .sort("time", -1)
            .limit(count)
        )
        for status in await cursor.to_list(None):
            statuses.append(status)
        return statuses

    @classmethod
    async def get_status_by_type(
        cls: Any, db: Any, event_id: str, status_type: str, count: int
    ) -> List[dict]:  # pragma: no cover
        """Get latest status function."""
        statuses: List = []
        cursor = (
            db.status_collection.find({"type": status_type, "event_id": event_id})
            .sort("time", -1)
            .limit(count)
        )
        for status in await cursor.to_list(None):
            statuses.append(status)
        return statuses

    @classmethod
    async def delete_status(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get status function."""
        result = await db.status_collection.delete_one({"id": id})
        return result
