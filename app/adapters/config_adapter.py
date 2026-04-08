"""Module for config adapter."""

import logging
from typing import Any


class ConfigAdapter:
    """Class representing an adapter for configs."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def create_config(cls, config: dict) -> str:  # pragma: no cover
        """Create config function."""
        return await cls.database.configs_collection.insert_one(config)

    @classmethod
    async def get_all_configs(cls) -> list[dict]:  # pragma: no cover
        """Get all configs function."""
        cursor = cls.database.configs_collection.find()
        return await cursor.to_list(None)

    @classmethod
    async def get_all_configs_by_event(cls, event_id: str) -> list[dict]:  # pragma: no cover
        """Get all configs by event function."""
        cursor = cls.database.configs_collection.find({"event_id": event_id})
        return await cursor.to_list(None)

    @classmethod
    async def get_config_by_key(cls, event_id: str, key: str) -> dict:  # pragma: no cover
        """Get config by key function."""
        return await cls.database.configs_collection.find_one(
            {"$and": [{"event_id": event_id}, {"key": key}]}
        )

    @classmethod
    async def get_config_by_id(cls, c_id: str) -> dict:  # pragma: no cover
        """Get config by id function."""
        return await cls.database.configs_collection.find_one({"id": c_id})

    @classmethod
    async def update_config(cls, c_id: str, config: dict) -> str | None:  # pragma: no cover
        """Update config function."""
        return await cls.database.configs_collection.replace_one({"id": c_id}, config)

    @classmethod
    async def delete_config(cls, c_id: str) -> str | None:  # pragma: no cover
        """Delete config function."""
        return await cls.database.configs_collection.delete_one({"id": c_id})
