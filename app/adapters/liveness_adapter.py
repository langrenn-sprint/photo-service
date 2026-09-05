"""Module for liveness adapter."""

import logging
from typing import Any


class LivenessAdapter:
    """Class representing an adapter for liveness checks."""

    database: Any
    logger: logging.Logger

    @classmethod
    async def init(cls, database: Any) -> None:  # pragma: no cover
        """Initialize the adapter with a database connection."""
        cls.database = database
        cls.logger = logging.getLogger("uvicorn.error")

    @classmethod
    async def is_ready(cls) -> bool:  # pragma: no cover
        """Check if the database is ready."""
        try:
            await cls.database.command("ping")
        except Exception:
            return False
        else:
            return True
