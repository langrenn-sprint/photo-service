"""Router module for status resources."""

import json
import logging
import os
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
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
    eventId: str,
    count: int = 25,
    type: str | None = None,
) -> Response:
    """Get status route function."""
    if type is not None:
        status_list = await StatusService.get_all_status_by_type(eventId, type, count)
    else:
        status_list = await StatusService.get_all_status(eventId, count)
    _list = [s.model_dump() for s in status_list]
    body = json.dumps(_list, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")


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
    "/status/{statusId}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.StatusAdmin]))],
)
async def delete_status(statusId: str) -> Response:
    """Delete status route function."""
    logging.debug(f"Got delete request for status {statusId}")
    try:
        await StatusService.delete_status(statusId)
    except StatusNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)
