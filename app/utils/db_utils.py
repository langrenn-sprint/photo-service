"""Drop db and recreate indexes."""

from typing import Any


async def drop_db_and_recreate_indexes(mongo: Any, db_name: str) -> None:
    """Drop db and recreate indexes."""
    await drop_db(mongo, db_name)


async def drop_db(mongo: Any, db_name: str) -> None:
    """Drop db."""
    await mongo.drop_database(f"{db_name}")
