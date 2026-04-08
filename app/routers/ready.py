"""Router module for ready resource."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/ready", response_class=PlainTextResponse)
async def ready() -> str:
    """Ready route function."""
    return "OK"
