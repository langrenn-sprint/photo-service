"""Router module for config resources."""

import json
import logging
import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.authorization import RoleChecker, UserRole
from app.models import Config
from app.services import (
    ConfigNotFoundError,
    ConfigService,
    IllegalValueError,
)

HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"

router = APIRouter()


@router.get("/config")
async def get_config(key: str, event_id: Annotated[str, Query(alias="eventId")]) -> Response:
    """Get config by key route function."""
    try:
        config = await ConfigService.get_config_by_key(event_id, key)
    except ConfigNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    body = config.model_dump_json()
    return Response(status_code=200, content=body, media_type="application/json")


@router.post(
    "/config",
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.ConfigAdmin]))],
)
async def create_config(config: Config) -> Response:
    """Create config route function."""
    logging.debug(f"Got create request for config {config} of type {type(config)}")
    try:
        config_id = await ConfigService.create_config(config)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    if config_id:
        logging.debug(f"inserted document with config_id {config_id}")
        return Response(
            status_code=201,
            headers={"Location": f"{BASE_URL}/config/{config_id}"},
        )
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST) from None


@router.put(
    "/config",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.ConfigAdmin]))],
)
async def update_config(config: Config) -> Response:
    """Update config route function."""
    logging.debug(f"Got put request for config {config} of type {type(config)}")
    try:
        await ConfigService.update_config(config)
    except IllegalValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except ConfigNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.delete(
    "/config/{config_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.Admin, UserRole.ConfigAdmin]))],
)
async def delete_config(config_id: str) -> Response:
    """Delete config route function."""
    logging.debug(f"Got delete request for config {config_id}")
    try:
        await ConfigService.delete_config(config_id)
    except ConfigNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    return Response(status_code=204)


@router.get("/configs")
async def get_configs(event_id: Annotated[str | None, Query(alias="eventId")] = None) -> Response:
    """Get all configs route function."""
    configs = await ConfigService.get_all_configs(event_id)
    _list = [c.model_dump() for c in configs]
    body = json.dumps(_list, default=str, ensure_ascii=False)
    return Response(status_code=200, content=body, media_type="application/json")
