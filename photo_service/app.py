"""Module for admin of photo service."""
import logging
import os
from typing import Any

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware
import motor.motor_asyncio

from .views import (
    AlbumsView,
    AlbumView,
    GooglePhotosView,
    PhotosView,
    PhotoView,
    Ping,
    Ready,
    VideoEventsView,
)


LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 27017))
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


async def create_app() -> web.Application:
    """Create an web application."""
    app = web.Application(
        middlewares=[
            cors_middleware(allow_all=True),
            error_middleware(),  # default error handler for whole application
        ]
    )
    # Set up logging
    logging.basicConfig(level=LOGGING_LEVEL)
    logging.getLogger("chardet.charsetprober").setLevel(LOGGING_LEVEL)

    # Set up routes:
    app.add_routes(
        [
            web.view("/albums", AlbumsView),
            web.view("/albums/{albumId}", AlbumView),
            web.view("/g_photos", GooglePhotosView),
            web.view("/g_photos/{albumId}", GooglePhotosView),
            web.view("/ping", Ping),
            web.view("/ready", Ready),
            web.view("/photos", PhotosView),
            web.view("/photos/{photoId}", PhotoView),
            web.view("/video_events", VideoEventsView),
        ]
    )

    async def mongo_context(app: Any) -> Any:
        # Set up database connection:
        logging.debug(f"Connecting to db at {DB_HOST}:{DB_PORT}")
        mongo = motor.motor_asyncio.AsyncIOMotorClient(
            host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASSWORD
        )
        db = mongo.DB_NAME
        app["db"] = db

        yield

        mongo.close()

    app.cleanup_ctx.append(mongo_context)

    return app
