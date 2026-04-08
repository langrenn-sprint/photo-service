"""Package for all adapters."""

from .albums_adapter import AlbumsAdapter
from .config_adapter import ConfigAdapter
from .liveness_adapter import LivenessAdapter
from .photos_adapter import PhotosAdapter
from .service_instances_adapter import ServiceInstancesAdapter
from .status_adapter import StatusAdapter

__all__ = [
    "AlbumsAdapter",
    "ConfigAdapter",
    "LivenessAdapter",
    "PhotosAdapter",
    "ServiceInstancesAdapter",
    "StatusAdapter",
]
