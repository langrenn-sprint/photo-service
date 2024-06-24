"""Module for config adapter."""
from typing import Any, List, Optional

from .adapter import Adapter


class ConfigAdapter(Adapter):
    """Class representing an adapter for sync-ed configs."""

    @classmethod
    async def create_config(cls: Any, db: Any, config: dict) -> str:  # pragma: no cover
        """Create config function."""
        result = await db.configs_collection.insert_one(config)
        return result

    @classmethod
    async def get_all_configs(cls: Any, db: Any) -> List:  # pragma: no cover
        """Get all configs function."""
        configs: List = []
        cursor = db.configs_collection.find()
        for config in await cursor.to_list(None):
            configs.append(config)
        return configs

    @classmethod
    async def get_config_by_key(
        cls: Any, db: Any, event_id: str, key: str
    ) -> dict:  # pragma: no cover
        """Get config function."""
        result = await db.configs_collection.find_one(
            {"key": key, "event_id": event_id}
        )
        return result

    @classmethod
    async def get_config_by_id(cls: Any, db: Any, id: str) -> dict:  # pragma: no cover
        """Get config function."""
        result = await db.configs_collection.find_one({"id": id})
        return result

    @classmethod
    async def update_config(
        cls: Any, db: Any, id: str, config: dict
    ) -> Optional[str]:  # pragma: no cover
        """Get config function."""
        result = await db.configs_collection.replace_one({"id": id}, config)
        return result

    @classmethod
    async def delete_config(
        cls: Any, db: Any, id: str
    ) -> Optional[str]:  # pragma: no cover
        """Get config function."""
        result = await db.configs_collection.delete_one({"id": id})
        return result
