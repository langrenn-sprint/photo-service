"""Conftest module."""

import os
import time
from http import HTTPStatus

import pytest
import requests
from fastapi.testclient import TestClient
from requests.exceptions import ConnectionError as _ConnectionError

from app import api

HOST_PORT = int(os.getenv("HOST_PORT", "8080"))


@pytest.fixture
def client() -> TestClient:
    """Instantiate server and start it."""
    return TestClient(api)


def is_responsive(url: str) -> bool:
    """Return true if response from service is 200."""
    url = f"{url}/ready"
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == HTTPStatus.OK:
            time.sleep(2)
            return True
    except _ConnectionError:
        return False
    return False


@pytest.fixture(scope="session")
def http_service(docker_ip: str, docker_services: object) -> str:
    """Ensure that HTTP service is up and responsive."""
    port = docker_services.port_for("photo-service", HOST_PORT)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: object) -> str:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")


@pytest.fixture(scope="session")
def docker_cleanup(pytestconfig: object) -> str:
    """Override default location of docker-compose.yml file."""
    return "stop"
