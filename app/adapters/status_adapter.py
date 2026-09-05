"""Module for status adapter."""

import logging
from typing import Any


class StatusAdapter:
    """Class representing an adapter for status messages."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def create_status(cls, status: dict) -> str:  # pragma: no cover
        """Create status function."""
        return await cls.database.status_collection.insert_one(status)

    @classmethod
    async def get_status_by_id(cls, c_id: str) -> dict:  # pragma: no cover
        """Get status by id function."""
        return await cls.database.status_collection.find_one({"id": c_id})

    @classmethod
    async def get_all_status(
        cls, event_id: str, count: int
    ) -> list[dict]:  # pragma: no cover
        """Get latest status function."""
        try:
            cursor = (
                cls.database.status_collection.find({"event_id": event_id})
                .sort("time", -1)
                .limit(count)
            )
            return await cursor.to_list(None)
        except Exception:
            err_msg = f"Error occurred while fetching status by event: {event_id}"
            logging.exception(err_msg)
        return []

    @classmethod
    async def get_all_status_by_type(
        cls, event_id: str, status_type: str, count: int
    ) -> list[dict]:  # pragma: no cover
        """Get latest status by type function."""
        try:
            cursor = (
                cls.database.status_collection.find(
                    {"type": status_type, "event_id": event_id}
                )
                .sort("time", -1)
                .limit(count)
            )
            return await cursor.to_list(None)
        except Exception:
            err_msg = f"Error occurred while fetching status by type: {status_type}"
            logging.exception(err_msg)
        return []

    @classmethod
    async def delete_status(cls, c_id: str) -> str | None:  # pragma: no cover
        """Delete status function."""
        return await cls.database.status_collection.delete_one({"id": c_id})
