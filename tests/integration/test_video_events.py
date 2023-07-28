"""Integration test cases for the video_events route."""
import os

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
import jwt
import pytest
from pytest_mock import MockFixture


@pytest.fixture
def token() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": os.getenv("ADMIN_USERNAME"), "roles": ["admin"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
def token_unsufficient_role() -> str:
    """Create a valid token."""
    secret = os.getenv("JWT_SECRET")
    algorithm = "HS256"
    payload = {"identity": "user", "roles": ["user"]}
    return jwt.encode(payload, secret, algorithm)  # type: ignore


@pytest.fixture
async def video_event() -> dict:
    """An video_event object for testing."""
    return {
        "_id": "64bede4190d55e1d205e8a0d",
        "events": [
            {
                "id": "3733eb36935e4d73800a9cf36185d5a2",
                "type": "personLineEvent",
                "detectionIds": ["90d55bfc64c54bfd98226697ad8445ca"],
                "properties": {
                    "trackingId": "90d55bfc64c54bfd98226697ad8445ca",
                    "status": "CrossLeft",
                },
                "zone": "doorcamera",
            }
        ],
        "sourceInfo": {
            "id": "camera_id",
            "timestamp": "2023-07-24T22:24:41.674323",
            "width": 608,
            "height": 342,
            "frameId": "1340",
            "imagePath": "",
        },
        "detections": [
            {
                "type": "person",
                "id": "90d55bfc64c54bfd98226697ad8445ca",
                "region": {
                    "type": "RECTANGLE",
                    "points": [
                        {"x": 0.491627341822574, "y": 0.2385801348769874},
                        {"x": 0.588894994635331, "y": 0.6395559924387793},
                    ],
                },
                "confidence": 0.9005028605461121,
                "metadata": {
                    "centerGroundPointX": "2.6310102939605713",
                    "centerGroundPointY": "18.635927200317383",
                    "groundOrientationAngle": "1.3",
                    "trackingId": "90d55bfc64c54bfd98226697ad8445ca",
                    "speed": "1.2",
                    "footprintX": "0.7306610584259033",
                    "footprintY": "0.8814966493381893",
                },
                "attributes": [{"label": "face_mask", "confidence": 0.99, "task": ""}],
            }
        ],
        "schemaVersion": "2.0",
    }


# Forbidden:
@pytest.mark.integration
async def test_create_video_events_insufficient_role(
    client: _TestClient,
    mocker: MockFixture,
    token_unsufficient_role: MockFixture,
    video_event: dict,
) -> None:
    """Should return 403 Forbidden."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "test_event_id"

    mocker.patch(
        "photo_service.adapters.video_events_adapter.VideoEventsAdapter.create_video_event",
        return_value=ID,
    )

    request_body = video_event

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token_unsufficient_role}",
    }
    url = f"/video_events?eventId={event_id}&queueName=video_events"

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=403)
        resp = await client.post(url, headers=headers, json=request_body)
        assert resp.status == 403


# No connection:
@pytest.mark.integration
async def test_create_video_event_no_connection(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    video_event: dict,
) -> None:
    """Should return 400 error, no conncetion to Azure service bus."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "test_event_id"
    mocker.patch(
        "photo_service.adapters.video_events_adapter.VideoEventsAdapter.create_video_event",
        return_value=ID,
    )

    request_body = video_event

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    url = f"/video_events?eventId={event_id}&queueName=video_events"

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post(url, headers=headers, json=request_body)
        assert resp.status == 400


# No connection:
@pytest.mark.integration
async def test_create_video_event_missing_input(
    client: _TestClient,
    mocker: MockFixture,
    token: MockFixture,
    video_event: dict,
) -> None:
    """Should return 400 error, http bad request."""
    ID = "290e70d5-0933-4af0-bb53-1d705ba7eb95"
    event_id = "test_event_id"
    mocker.patch(
        "photo_service.adapters.video_events_adapter.VideoEventsAdapter.create_video_event",
        return_value=ID,
    )

    request_body = video_event

    headers = {
        hdrs.CONTENT_TYPE: "application/json",
        hdrs.AUTHORIZATION: f"Bearer {token}",
    }
    url = f"/video_events?eventId={event_id}"

    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        m.post("http://example.com:8081/authorize", status=204)
        resp = await client.post(url, headers=headers, json=request_body)
        assert resp.status == 400
