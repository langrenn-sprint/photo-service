"""Contract test cases for ready."""

from http import HTTPStatus
from typing import Any

import httpx
import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_ready(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/ready"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.text == "OK"
