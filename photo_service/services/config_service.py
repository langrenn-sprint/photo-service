"""Module for config service."""

import logging
import uuid
from typing import Any

from photo_service.adapters import ConfigAdapter
from photo_service.models import Config

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create an uuid."""
    return str(uuid.uuid4())


class ConfigNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class ConfigService:
    """Class representing a service for config."""

    @classmethod
    async def get_all_configs(
        cls: Any, db: Any, event_id: str | None = None
    ) -> list[Config]:
        """Get all config function."""
        if event_id:
            _config = await ConfigAdapter.get_all_configs_by_event(db, event_id)
        else:
            _config = await ConfigAdapter.get_all_configs(db)
        return [Config.from_dict(e) for e in _config]

    @classmethod
    async def create_config(cls: Any, db: Any, config: Config) -> str | None:
        """Create config function.

        Args:
            db (Any): the db
            config (Config): a config instanse to be created

        Returns:
            Optional[str]: The id of the created config. None otherwise.

        Raises:
            IllegalValueError: input object has illegal values

        """
        # Validation:
        if config.id:
            err_msg = "Cannot create config with input id."
            raise IllegalValueError(err_msg) from None
        old_config = await ConfigAdapter.get_config_by_key(
            db, config.event_id, config.key
        )
        if old_config:
            err_msg = (
                f"Config with key {config.key} already exists on event {config.event_id}"
            )
            raise IllegalValueError(err_msg) from None

        # create id
        c_id = create_id()
        config.id = c_id
        # insert new config
        new_config = config.to_dict()
        result = await ConfigAdapter.create_config(db, new_config)
        logging.debug(f"inserted config with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_config_by_id(cls: Any, db: Any, c_id: str) -> Config:
        """Get config function."""
        config = await ConfigAdapter.get_config_by_id(db, c_id)
        # return the document if found:
        if config:
            return Config.from_dict(config)
        err_msg = f"Config with id {c_id} not found"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def get_config_by_key(cls: Any, db: Any, event_id: str, key: str) -> Config:
        """Get config function."""
        config = await ConfigAdapter.get_config_by_key(db, event_id, key)
        # return the document if found:
        if config:
            return Config.from_dict(config)
        err_msg = f"Config with key {key} not found on event {event_id}"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def update_config(cls: Any, db: Any, config: Config) -> str | None:
        """Get config function."""
        # get old document
        old_config = await ConfigAdapter.get_config_by_key(
            db, config.event_id, config.key
        )
        # update the config if found:
        if old_config:
            config.id = old_config["id"]
            body = config.to_dict()
            return await ConfigAdapter.update_config(db, old_config["id"], body)
        err_msg = f"Config with key {config.key} not found on event {config.event_id}"
        raise ConfigNotFoundError(err_msg) from None

    @classmethod
    async def delete_config(cls: Any, db: Any, c_id: str) -> str | None:
        """Get config function."""
        # get old document
        config = await ConfigAdapter.get_config_by_id(db, c_id)
        # delete the document if found:
        if config:
            return await ConfigAdapter.delete_config(db, c_id)
        err_msg = f"Config with id {c_id} not found"
        raise ConfigNotFoundError(err_msg) from None
