"""Module for service instances service."""

import logging
import uuid

from app.adapters import ServiceInstancesAdapter
from app.models import ServiceInstance

from .exceptions import IllegalValueError


def create_id() -> str:  # pragma: no cover
    """Create a uuid."""
    return str(uuid.uuid4())


class ServiceInstanceNotFoundError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class ServiceInstancesService:
    """Class representing a service for service instances."""

    @classmethod
    async def get_all_service_instances(cls, event_id: str) -> list[ServiceInstance]:
        """Get all service instances function."""
        _service_instances = await ServiceInstancesAdapter.get_all_service_instances(
            event_id
        )
        service_instances = [
            ServiceInstance.model_validate(e) for e in _service_instances
        ]
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
        cls, event_id: str, service_type: str
    ) -> list[ServiceInstance]:
        """Get all service instances for one service_type function."""
        _service_instances = (
            await ServiceInstancesAdapter.get_service_instances_by_service_type(
                event_id, service_type
            )
        )
        service_instances = [
            ServiceInstance.model_validate(e) for e in _service_instances
        ]
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
        cls, event_id: str, status: str
    ) -> list[ServiceInstance]:
        """Get all service instances for one status function."""
        _service_instances = (
            await ServiceInstancesAdapter.get_service_instances_by_status(
                event_id, status
            )
        )
        service_instances = [
            ServiceInstance.model_validate(e) for e in _service_instances
        ]
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
        cls, service_instance: ServiceInstance
    ) -> str | None:
        """Create service instance function."""
        if service_instance.id:
            err_msg = "Cannot create service instance with input id."
            raise IllegalValueError(err_msg) from None
        c_id = create_id()
        service_instance.id = c_id
        new_service_instance = service_instance.model_dump()
        result = await ServiceInstancesAdapter.create_service_instance(
            new_service_instance
        )
        logging.debug(f"inserted service instance with id: {c_id}")
        if result:
            return c_id
        return None

    @classmethod
    async def get_service_instance_by_id(cls, c_id: str) -> ServiceInstance:
        """Get service instance by id function."""
        service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            c_id
        )
        if service_instance:
            return ServiceInstance.model_validate(service_instance)
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None

    @classmethod
    async def update_service_instance(
        cls, c_id: str, service_instance: ServiceInstance
    ) -> str | None:
        """Update service instance function."""
        old_service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            c_id
        )
        if old_service_instance:
            if service_instance.id != old_service_instance["id"]:
                err_msg = "Cannot change id for service instance."
                raise IllegalValueError(err_msg) from None
            new_service_instance = service_instance.model_dump()
            return await ServiceInstancesAdapter.update_service_instance(
                c_id, new_service_instance
            )
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None

    @classmethod
    async def delete_service_instance(cls, c_id: str) -> str | None:
        """Delete service instance function."""
        service_instance = await ServiceInstancesAdapter.get_service_instance_by_id(
            c_id
        )
        if service_instance:
            return await ServiceInstancesAdapter.delete_service_instance(c_id)
        err_msg = f"Service instance with id {c_id} not found."
        raise ServiceInstanceNotFoundError(err_msg) from None
