"""Service instance data class module."""

from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import DataClassJsonMixin, config
from marshmallow import fields


def datetime_encoder(dt: datetime | None) -> str | None:
    """Encode datetime to ISO format string, handling None."""
    return dt.isoformat() if dt is not None else None


def datetime_decoder(dt_str: str | None) -> datetime | None:
    """Decode ISO format string to datetime, handling None."""
    return datetime.fromisoformat(dt_str) if dt_str is not None else None


@dataclass
class ServiceInstance(DataClassJsonMixin):
    """Data class representing a running service instance."""

    service_type: str  # e.g., "video-service", "integration-service"
    instance_name: str
    status: str  # e.g., "running", "waiting", "error"
    host_name: str
    port: int
    event_id: str | None = field(default=None)
    id: str | None = field(default=None)
    started_at: datetime | None = field(
        default=None,
        metadata=config(
            encoder=datetime_encoder,
            decoder=datetime_decoder,
            mm_field=fields.DateTime(format="iso"),
        ),
    )
    last_heartbeat: datetime | None = field(
        default=None,
        metadata=config(
            encoder=datetime_encoder,
            decoder=datetime_decoder,
            mm_field=fields.DateTime(format="iso"),
        ),
    )
    metadata: dict | None = field(default=None)
