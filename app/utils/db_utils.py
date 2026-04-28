"""Database utility functions."""

from typing import Any


async def drop_db_and_recreate_indexes(mongo: Any, db_name: str) -> None:
    """Drop the database. Note: index recreation is not implemented."""
    await drop_db(mongo, db_name)


async def drop_db(mongo: Any, db_name: str) -> None:
    """Drop db."""
    await mongo.drop_database(f"{db_name}")
