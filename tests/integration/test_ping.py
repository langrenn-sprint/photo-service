"""Integration test cases for the ping route."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_ping(client: TestClient) -> None:
    """Should return OK."""
    resp = client.get("/ping")
    assert resp.status_code == HTTPStatus.OK
    assert "OK" in resp.text
