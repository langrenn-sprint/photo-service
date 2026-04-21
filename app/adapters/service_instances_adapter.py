"""Module for service instances adapter."""

import logging
from typing import Any


class ServiceInstancesAdapter:
    """Class representing an adapter for service instances."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def create_service_instance(
        cls, service_instance: dict
    ) -> str:  # pragma: no cover
        """Create service instance function."""
        return await cls.database.service_instances_collection.insert_one(
            service_instance
        )

    @classmethod
    async def get_all_service_instances(cls, event_id: str) -> list:  # pragma: no cover
        """Get all service instances function."""
        cursor = cls.database.service_instances_collection.find(
            {"event_id": event_id}
        ).sort("started_at", -1)
        return await cursor.to_list(None)

    @classmethod
    async def get_service_instance_by_id(cls, c_id: str) -> dict:  # pragma: no cover
        """Get service instance by id function."""
        return await cls.database.service_instances_collection.find_one({"id": c_id})

    @classmethod
    async def get_service_instances_by_service_type(
        cls, event_id: str, service_type: str
    ) -> list:  # pragma: no cover
        """Get all service instances by service_type function."""
        cursor = cls.database.service_instances_collection.find(
            {"service_type": service_type, "event_id": event_id}
        ).sort("started_at", -1)
        return await cursor.to_list(None)

    @classmethod
    async def get_service_instances_by_status(
        cls, event_id: str, status: str
    ) -> list:  # pragma: no cover
        """Get all service instances by status function."""
        cursor = cls.database.service_instances_collection.find(
            {"status": status, "event_id": event_id}
        ).sort("started_at", -1)
        return await cursor.to_list(None)

    @classmethod
    async def update_service_instance(
        cls, c_id: str, service_instance: dict
    ) -> str | None:  # pragma: no cover
        """Update service instance function."""
        return await cls.database.service_instances_collection.replace_one(
            {"id": c_id}, service_instance
        )

    @classmethod
    async def delete_service_instance(cls, c_id: str) -> str | None:  # pragma: no cover
        """Delete service instance function."""
        return await cls.database.service_instances_collection.delete_one({"id": c_id})
