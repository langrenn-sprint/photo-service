"""Module for admin of photo service."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import motor.motor_asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .adapters import (
    AlbumsAdapter,
    ConfigAdapter,
    LivenessAdapter,
    PhotosAdapter,
    ServiceInstancesAdapter,
    StatusAdapter,
)
from .authorization import (
    TokenError,
    TokenMissingError,
    TokenValidationError,
)
from .routers import albums, config, g_photos, photos, ping, ready, service_instances, status

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "27017"))
DB_NAME = os.getenv("DB_NAME", "photo_service")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


class EndpointFilter(logging.Filter):
    def __init__(self, excluded_endpoints: list[str]) -> None:
        super().__init__()
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover
        if (
            record.args
            and len(record.args) >= 3
            and record.args[2] in self.excluded_endpoints
        ):
            return False
        return True


logger = logging.getLogger("uvicorn.error")
access_logger = logging.getLogger("uvicorn.access")
excluded_endpoints = ["/ping", "/ready"]
access_logger.addFilter(EndpointFilter(excluded_endpoints))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001  # pragma: no cover
    logger.debug(f"Connecting to db at {DB_HOST}:{DB_PORT}")
    mongo = motor.motor_asyncio.AsyncIOMotorClient(
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USER,
        password=DB_PASSWORD,
        uuidRepresentation="standard",
    )
    db = mongo[f"{DB_NAME}"]

    await LivenessAdapter.init(db)
    await PhotosAdapter.init(db)
    await AlbumsAdapter.init(db)
    await ConfigAdapter.init(db)
    await ServiceInstancesAdapter.init(db)
    await StatusAdapter.init(db)

    yield

    mongo.close()


api = FastAPI(
    lifespan=lifespan,
    title="Photo Service",
    version="1.0.0",
    separate_input_output_schemas=False,
)


@api.exception_handler(TokenError)
async def token_exception_handler(request: Request, exc: TokenError) -> JSONResponse:  # pragma: no cover
    _ = request
    if isinstance(exc, TokenMissingError):
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    if isinstance(exc, TokenValidationError):
        return JSONResponse(status_code=403, content={"detail": "Not authorized to access this resource"})
    return JSONResponse(status_code=403, content={"detail": "Not authorized to access this resource"})


api.include_router(ping.router)
api.include_router(ready.router)
api.include_router(photos.router)
api.include_router(albums.router)
api.include_router(config.router)
api.include_router(service_instances.router)
api.include_router(status.router)
api.include_router(g_photos.router)
