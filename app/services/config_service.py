"""Module for config service."""

import logging
import uuid

from app.adapters import ConfigAdapter
from app.models import Config

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create a uuid."""
    return str(uuid.uuid4())


class ConfigNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class ConfigService:
    """Class representing a service for config."""

    @classmethod
    async def get_all_configs(cls, event_id: str | None = None) -> list[Config]:
        """Get all configs function."""
        if event_id:
            _config = await ConfigAdapter.get_all_configs_by_event(event_id)
        else:
            _config = await ConfigAdapter.get_all_configs()
        return [Config.model_validate(e) for e in _config]

    @classmethod
    async def create_config(cls, config: Config) -> str | None:
        """Create config function."""
        if config.id:
            err_msg = "Cannot create config with input id."
            raise IllegalValueError(err_msg) from None
        old_config = await ConfigAdapter.get_config_by_key(config.event_id, config.key)
        if old_config:
            err_msg = f"Config with key {config.key} already exists on event {config.event_id}"
            raise IllegalValueError(err_msg) from None
        c_id = create_id()
        config.id = c_id
        new_config = config.model_dump()
        result = await ConfigAdapter.create_config(new_config)
        logging.debug(f"inserted config with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_config_by_id(cls, c_id: str) -> Config:
        """Get config by id function."""
        config = await ConfigAdapter.get_config_by_id(c_id)
        if config:
            return Config.model_validate(config)
        err_msg = f"Config with id {c_id} not found"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def get_config_by_key(cls, event_id: str, key: str) -> Config:
        """Get config by key function."""
        config = await ConfigAdapter.get_config_by_key(event_id, key)
        if config:
            return Config.model_validate(config)
        err_msg = f"Config with key {key} not found on event {event_id}"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def update_config(cls, config: Config) -> str | None:
        """Update config function."""
        old_config = await ConfigAdapter.get_config_by_key(config.event_id, config.key)
        if old_config:
            config.id = old_config["id"]
            body = config.model_dump()
            return await ConfigAdapter.update_config(old_config["id"], body)
        err_msg = f"Config with key {config.key} not found on event {config.event_id}"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def delete_config(cls, c_id: str) -> str | None:
        """Delete config function."""
        config = await ConfigAdapter.get_config_by_id(c_id)
        if config:
            return await ConfigAdapter.delete_config(c_id)
        err_msg = f"Config with id {c_id} not found"
        raise ConfigNotFoundError(err_msg) from None
