"""Module for status service."""

import logging
import uuid
from typing import Any

from photo_service.adapters import StatusAdapter
from photo_service.models import Status

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create an uuid."""
    return str(uuid.uuid4())


class StatusNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class StatusService:
    """Class representing a service for status."""

    @classmethod
    async def create_status(cls: Any, db: Any, status: Status) -> str | None:
        """Create status function.

        Args:
            db (Any): the db
            status (Status): a status instanse to be created

        Returns:
            Optional[str]: The id of the created status. None otherwise.

        Raises:
            IllegalValueError: input object has illegal values

        """
        # Validation:
        if status.id:
            err_msg = "Cannot create status with input id."
            raise IllegalValueError(err_msg) from None
        # create id
        s_id = create_id()
        status.id = s_id
        # insert new status
        new_status = status.to_dict()
        result = await StatusAdapter.create_status(db, new_status)
        logging.debug(f"inserted status with id: {s_id}")
        if result:
            return s_id
        return None

    @classmethod
    async def get_all_status(
        cls: Any, db: Any, event_id: str, count: int
    ) -> list[Status]:
        """Get all status function."""
        _status = await StatusAdapter.get_all_status(db, event_id, count)
        return [Status.from_dict(e) for e in _status]

    @classmethod
    async def get_all_status_by_type(
        cls: Any, db: Any, event_id: str, status_type: str, count: int
    ) -> list[Status]:
        """Get status function."""
        _status = await StatusAdapter.get_all_status_by_type(db, event_id, status_type, count)
        return [Status.from_dict(e) for e in _status]

    @classmethod
    async def delete_status(cls: Any, db: Any, c_id: str) -> str | None:
        """Get status function."""
        # get old document
        status = await StatusAdapter.get_status_by_id(db, c_id)
        # delete the document if found:
        if status:
            return await StatusAdapter.delete_status(db, c_id)
        err_msg = f"Status with id {c_id} not found"
        raise StatusNotFoundError(err_msg) from None
