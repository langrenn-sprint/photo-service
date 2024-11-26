"""Module for status service."""

import logging
from typing import Any, List, Optional
import uuid

from photo_service.adapters import StatusAdapter
from photo_service.models import Status
from .exceptions import IllegalValueException


def create_id() -> str:  # pragma: no cover
    """Creates an uuid."""
    return str(uuid.uuid4())


class StatusNotFoundException(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class StatusService:
    """Class representing a service for status."""

    @classmethod
    async def create_status(cls: Any, db: Any, status: Status) -> Optional[str]:
        """Create status function.

        Args:
            db (Any): the db
            status (Status): a status instanse to be created

        Returns:
            Optional[str]: The id of the created status. None otherwise.

        Raises:
            IllegalValueException: input object has illegal values
        """
        # Validation:
        if status.id:
            raise IllegalValueException("Cannot create status with input id.") from None
        # create id
        id = create_id()
        status.id = id
        # insert new status
        new_status = status.to_dict()
        result = await StatusAdapter.create_status(db, new_status)
        logging.debug(f"inserted status with id: {id}")
        if result:
            return id
        return None

    @classmethod
    async def get_all_status(
        cls: Any, db: Any, event_id: str, count: int
    ) -> List[Status]:
        """Get all status function."""
        status_list: List[Status] = []
        _status = await StatusAdapter.get_all_status(db, event_id, count)
        for e in _status:
            status_list.append(Status.from_dict(e))
        return status_list

    @classmethod
    async def get_all_status_by_type(
        cls: Any, db: Any, event_id: str, type: str, count: int
    ) -> List[Status]:
        """Get status function."""
        status_list: List[Status] = []
        _status = await StatusAdapter.get_all_status_by_type(db, event_id, type, count)
        for e in _status:
            status_list.append(Status.from_dict(e))
        return status_list

    @classmethod
    async def delete_status(cls: Any, db: Any, id: str) -> Optional[str]:
        """Get status function."""
        # get old document
        status = await StatusAdapter.get_status_by_id(db, id)
        # delete the document if found:
        if status:
            result = await StatusAdapter.delete_status(db, id)
            return result
        raise StatusNotFoundException(f"Status with id {id} not found") from None
