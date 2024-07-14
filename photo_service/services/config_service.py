"""Module for config service."""
import logging
from typing import Any, List, Optional
import uuid

from photo_service.adapters import ConfigAdapter
from photo_service.models import Config
from .exceptions import IllegalValueException


def create_id() -> str:  # pragma: no cover
    """Creates an uuid."""
    return str(uuid.uuid4())


class ConfigNotFoundException(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class ConfigService:
    """Class representing a service for config."""

    @classmethod
    async def get_all_configs(
        cls: Any, db: Any, event_id: Optional[str] = None
    ) -> List[Config]:
        """Get all config function."""
        config: List[Config] = []
        if event_id:
            _config = await ConfigAdapter.get_all_configs_by_event(db, event_id)
        else:
            _config = await ConfigAdapter.get_all_configs(db)
        for e in _config:
            config.append(Config.from_dict(e))
        return config

    @classmethod
    async def create_config(cls: Any, db: Any, config: Config) -> Optional[str]:
        """Create config function.

        Args:
            db (Any): the db
            config (Config): a config instanse to be created

        Returns:
            Optional[str]: The id of the created config. None otherwise.

        Raises:
            IllegalValueException: input object has illegal values
        """
        # Validation:
        if config.id:
            raise IllegalValueException("Cannot create config with input id.") from None
        old_config = await ConfigAdapter.get_config_by_key(
            db, config.event_id, config.key
        )
        if old_config:
            raise IllegalValueException(
                f"Config with key {config.key} already exists on event {config.event_id}"
            ) from None

        # create id
        id = create_id()
        config.id = id
        # insert new config
        new_config = config.to_dict()
        result = await ConfigAdapter.create_config(db, new_config)
        logging.debug(f"inserted config with id: {id}")
        if result:
            return id
        return None

    @classmethod
    async def get_config_by_id(cls: Any, db: Any, id: str) -> Config:
        """Get config function."""
        config = await ConfigAdapter.get_config_by_id(db, id)
        # return the document if found:
        if config:
            return Config.from_dict(config)
        raise ConfigNotFoundException(f"Config with id {id} not found") from None

    @classmethod
    async def get_config_by_key(cls: Any, db: Any, event_id: str, key: str) -> Config:
        """Get config function."""
        config = await ConfigAdapter.get_config_by_key(db, event_id, key)
        # return the document if found:
        if config:
            return Config.from_dict(config)
        raise ConfigNotFoundException(
            f"Config with key {key} not found on event {event_id}"
        ) from None

    @classmethod
    async def update_config(cls: Any, db: Any, config: Config) -> Optional[str]:
        """Get config function."""
        # get old document
        old_config = await ConfigAdapter.get_config_by_key(
            db, config.event_id, config.key
        )
        # update the config if found:
        if old_config:
            config.id = old_config["id"]
            body = config.to_dict()
            result = await ConfigAdapter.update_config(db, old_config["id"], body)
            return result
        raise ConfigNotFoundException(f"Config {config} not found.") from None

    @classmethod
    async def delete_config(cls: Any, db: Any, id: str) -> Optional[str]:
        """Get config function."""
        # get old document
        config = await ConfigAdapter.get_config_by_id(db, id)
        # delete the document if found:
        if config:
            result = await ConfigAdapter.delete_config(db, id)
            return result
        raise ConfigNotFoundException(f"Config with id {id} not found") from None
