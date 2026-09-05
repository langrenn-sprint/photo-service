"""Service instance model module."""

from datetime import datetime

from pydantic import BaseModel


class ServiceInstance(BaseModel):
    """Model representing a running service instance."""

    service_type: str
    instance_name: str
    status: str
    host_name: str
    action: str
    event_id: str | None = None
    id: str | None = None
    started_at: datetime | None = None
    last_heartbeat: datetime | None = None
    metadata: dict | None = None
