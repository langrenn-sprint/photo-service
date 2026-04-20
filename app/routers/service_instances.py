"""Router module for service instances resources."""

import json
import logging
import os
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import Response

from app.authorization import RoleChecker, UserRole
from app.models import ServiceInstance
from app.services import (
    IllegalValueError,
    ServiceInstanceNotFoundError,
    ServiceInstancesService,
)

HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"

router = APIRouter()


@router.get("/service-instances")
async def get_service_instances(
    eventId: str = "",
    serviceType: str | None = None,
    status: str | None = None,
) -> Response:
    """Get service instances route function."""
    if serviceType is not None:
        service_instances = await ServiceInstancesService.get_service_instances_by_service_type(
            eventId, serviceType
        )
    elif status is not None:
        service_instances = await ServiceInstancesService.get_service_instances_by_status(
            eventId, status
        )
    else:
        service_instances = await ServiceInstancesService.get_all_service_instances(eventId)
    _list = [si.model_dump() for si in service_instances]
    body = json.dumps(_list, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")


@router.post(
    "/service-instances",
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def create_service_instance(service_instance: ServiceInstance) -> Response:
    """Create service instance route function."""
    logging.debug(
        f"Got create request for service instance {service_instance} of type {type(service_instance)}"
    )
    try:
        service_instance_id = await ServiceInstancesService.create_service_instance(service_instance)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    if service_instance_id:
        logging.debug(f"inserted document with service_instance_id {service_instance_id}")
        return Response(
            status_code=201,
            headers={"Location": f"{BASE_URL}/service-instances/{service_instance_id}"},
        )
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST) from None


@router.get("/service-instances/{serviceInstanceId}")
async def get_service_instance(serviceInstanceId: str) -> Response:
    """Get service instance by id route function."""
    logging.debug(f"Got get request for service instance {serviceInstanceId}")
    try:
        service_instance = await ServiceInstancesService.get_service_instance_by_id(serviceInstanceId)
    except ServiceInstanceNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    logging.debug(f"Got service instance: {service_instance}")
    body = service_instance.model_dump_json()
    return Response(status_code=200, content=body, media_type="application/json")


@router.put(
    "/service-instances/{serviceInstanceId}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def update_service_instance(
    service_instance: ServiceInstance,
    service_instance_id: str = Path(..., alias="serviceInstanceId"),
) -> Response:
    """Update service instance route function."""
    logging.debug(
        f"Got put request for service instance {service_instance} of type {type(service_instance)}"
    )
    try:
        await ServiceInstancesService.update_service_instance(service_instance_id, service_instance)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except ServiceInstanceNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.delete(
    "/service-instances/{serviceInstanceId}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.PhotoAdmin]))],
)
async def delete_service_instance(serviceInstanceId: str) -> Response:
    """Delete service instance route function."""
    logging.debug(f"Got delete request for service instance {serviceInstanceId}")
    try:
        await ServiceInstancesService.delete_service_instance(serviceInstanceId)
    except ServiceInstanceNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
