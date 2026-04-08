"""Module for status service."""

import logging
import uuid

from app.adapters import StatusAdapter
from app.models import Status

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create a uuid."""
    return str(uuid.uuid4())


class StatusNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class StatusService:
    """Class representing a service for status."""

    @classmethod
    async def create_status(cls, status: Status) -> str | None:
        """Create status function."""
        if status.id:
            err_msg = "Cannot create status with input id."
            raise IllegalValueError(err_msg) from None
        s_id = create_id()
        status.id = s_id
        new_status = status.model_dump()
        result = await StatusAdapter.create_status(new_status)
        logging.debug(f"inserted status with id: {s_id}")
        if result:
            return s_id
        return None

    @classmethod
    async def get_all_status(cls, event_id: str, count: int) -> list[Status]:
        """Get all status function."""
        _status = await StatusAdapter.get_all_status(event_id, count)
        return [Status.model_validate(e) for e in _status]

    @classmethod
    async def get_all_status_by_type(cls, event_id: str, status_type: str, count: int) -> list[Status]:
        """Get status by type function."""
        _status = await StatusAdapter.get_all_status_by_type(event_id, status_type, count)
        return [Status.model_validate(e) for e in _status]

    @classmethod
    async def delete_status(cls, c_id: str) -> str | None:
        """Delete status function."""
        status = await StatusAdapter.get_status_by_id(c_id)
        if status:
            return await StatusAdapter.delete_status(c_id)
        err_msg = f"Status with id {c_id} not found"
        raise StatusNotFoundError(err_msg) from None
