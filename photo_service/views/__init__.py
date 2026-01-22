"""Package for all views."""

from .albums import AlbumsView, AlbumView
from .config import ConfigsView, ConfigView
from .g_photos import GooglePhotosView
from .liveness import Ping, Ready
from .photos import PhotosView, PhotoView
from .service_instances import ServiceInstancesView, ServiceInstanceView
from .status import StatusView
from .unit_test import UnitTestView
