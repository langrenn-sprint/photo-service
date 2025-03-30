"""Module for config adapter."""

from typing import Any

from .adapter import Adapter


class ConfigAdapter(Adapter):
    """Class representing an adapter for photo configs."""

    @classmethod
    async def create_config(cls: Any, db: Any, config: dict) -> str:  # pragma: no cover
        """Create config function."""
        return await db.configs_collection.insert_one(config)

    @classmethod
    async def get_all_configs(cls: Any, db: Any) -> list[dict]:  # pragma: no cover
        """Get configs function."""
        return await db.configs_collection.find()

    @classmethod
    async def get_all_configs_by_event(
        cls: Any, db: Any, event_id: str
    ) -> list[dict]:  # pragma: no cover
        """Get configs function."""
        return await db.configs_collection.find(
            {"event_id": event_id}
        )

    @classmethod
    async def get_config_by_key(
        cls: Any, db: Any, event_id: str, key: str
    ) -> dict:  # pragma: no cover
        """Get config function."""
        return await db.configs_collection.find_one(
            {"$and": [{"event_id": event_id}, {"key": key}]}
        )

    @classmethod
    async def get_config_by_id(cls: Any, db: Any, c_id: str) -> dict:  # pragma: no cover
        """Get config function."""
        return await db.configs_collection.find_one({"id": c_id})

    @classmethod
    async def update_config(
        cls: Any, db: Any, c_id: str, config: dict
    ) -> str | None:  # pragma: no cover
        """Get config function."""
        return await db.configs_collection.replace_one({"id": c_id}, config)

    @classmethod
    async def delete_config(
        cls: Any, db: Any, c_id: str
    ) -> str | None:  # pragma: no cover
        """Get config function."""
        return await db.configs_collection.delete_one({"id": c_id})
