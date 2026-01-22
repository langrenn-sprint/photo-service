"""Module for service instances service."""

import logging
import uuid
from typing import Any

from photo_service.adapters import ServiceInstancesAdapter
from photo_service.models import ServiceInstance

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create an uuid."""
    return str(uuid.uuid4())


class ServiceInstanceNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class ServiceInstancesService:
    """Class representing a service for service instances."""

    @classmethod
    async def get_all_service_instances(
        cls: Any, db: Any, event_id: str
    ) -> list[ServiceInstance]:
        """Get all service instances function."""
        _service_instances = await ServiceInstancesAdapter.get_all_service_instances(
            db, event_id
        )
        service_instances = [ServiceInstance.from_dict(e) for e in _service_instances]
        return sorted(
            service_instances,
            key=lambda k: (
                k.started_at is not None,
                k.started_at,
            ),
            reverse=True,
        )

    @classmethod
    async def get_service_instances_by_service_type(
        cls: Any, db: Any, event_id: str, service_type: str
    ) -> list[ServiceInstance]:
        """Get all service instances for one service_type function."""
        _service_instances = (
            await ServiceInstancesAdapter.get_service_instances_by_service_type(
                db, event_id, service_type
            )
        )
        service_instances = [ServiceInstance.from_dict(e) for e in _service_instances]
        return sorted(
            service_instances,
            key=lambda k: (
                k.started_at is not None,
                k.started_at,
            ),
            reverse=True,
        )

    @classmethod
    async def get_service_instances_by_status(
        cls: Any, db: Any, event_id: str, status: str
    ) -> list[ServiceInstance]:
        """Get all service instances for one status function."""
        _service_instances = (
            await ServiceInstancesAdapter.get_service_instances_by_status(
                db, event_id, status
            )
        )
        service_instances = [ServiceInstance.from_dict(e) for e in _service_instances]
        return sorted(
            service_instances,
            key=lambda k: (
                k.started_at is not None,
                k.started_at,
            ),
            reverse=True,
        )

    @classmethod
    async def create_service_instance(
        cls: Any, db: Any, service_instance: ServiceInstance
    ) -> str | None:
        """Create service instance function.

        Args:
            db (Any): the db
            service_instance (ServiceInstance): a service instance to be created

        Returns:
            Optional[str]: The id of the created service instance. None otherwise.

        Raises:
            IllegalValueError: input object has illegal values

        """
        # Validation:
        if service_instance.id:
            err_msg = "Cannot create service instance with input id."
            raise IllegalValueError(err_msg) from None
        # create id
        c_id = create_id()
        service_instance.id = c_id
        # insert new service instance
        new_service_instance = service_instance.to_dict()
        result = await ServiceInstancesAdapter.create_service_instance(
            db, new_service_instance
        )
        logging.debug(f"inserted service instance with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_service_instance_by_id(
        cls: Any, db: Any, c_id: str
    ) -> ServiceInstance:
        """Get service instance function."""
        service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            db, c_id
        )
        # return the document if found:
        if service_instance:
            return ServiceInstance.from_dict(service_instance)
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None

    @classmethod
    async def update_service_instance(
        cls: Any, db: Any, c_id: str, service_instance: ServiceInstance
    ) -> str | None:
        """Update service instance function."""
        # get old document
        old_service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            db, c_id
        )
        # update the service instance if found:
        if old_service_instance:
            if service_instance.id != old_service_instance["id"]:
                err_msg = "Cannot change id for service instance."
                raise IllegalValueError(err_msg) from None
            new_service_instance = service_instance.to_dict()
            return await ServiceInstancesAdapter.update_service_instance(
                db, c_id, new_service_instance
            )
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None

    @classmethod
    async def delete_service_instance(cls: Any, db: Any, c_id: str) -> str | None:
        """Delete service instance function."""
        # get old document
        service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            db, c_id
        )
        # delete the document if found:
        if service_instance:
            return await ServiceInstancesAdapter.delete_service_instance(db, c_id)
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None
