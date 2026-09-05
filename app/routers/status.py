"""Router module for status resources."""

import json
import logging
import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.authorization import RoleChecker, UserRole
from app.models import Status
from app.services import (
    IllegalValueError,
    StatusNotFoundError,
    StatusService,
)

HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"

router = APIRouter()


@router.get("/status")
async def get_status(
    event_id: Annotated[str, Query(alias="eventId")],
    count: int = 25,
    status_type: Annotated[str | None, Query(alias="type")] = None,
) -> list[Status]:
    """Get status route function."""
    if status_type is not None:
        return await StatusService.get_all_status_by_type(event_id, status_type, count)
    return await StatusService.get_all_status(event_id, count)


@router.post(
    "/status",
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.StatusAdmin]))],
)
async def create_status(status: Status) -> Response:
    """Create status route function."""
    logging.debug(f"Got create request for status {status} of type {type(status)}")
    try:
        status_id = await StatusService.create_status(status)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    if status_id:
        logging.debug(f"inserted document with status_id {status_id}")
        return Response(
            status_code=201,
            headers={"Location": f"{BASE_URL}/status/{status_id}"},
        )
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST) from None


@router.delete(
    "/status/{status_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.StatusAdmin]))],
)
async def delete_status(status_id: str) -> Response:
    """Delete status route function."""
    logging.debug(f"Got delete request for status {status_id}")
    try:
        await StatusService.delete_status(status_id)
    except StatusNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
