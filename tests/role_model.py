"""The role model for photo-service, shared by the integration and contract tests.

See langrenn-sprint/event-service-gui#215. All GET operations are open. Every
write operation is listed here with the roles that may call it: admin, and the
photo-service role for that resource.
"""

ADMIN = "admin"
EVENT_ADMIN = "event-admin"
RESULT_ADMIN = "result-admin"
CONTESTANT_ADMIN = "contestant-admin"
# The roles user-service creates users with:
ROLES = [ADMIN, EVENT_ADMIN, RESULT_ADMIN, CONTESTANT_ADMIN]

# Roles only photo-service knows. user-service cannot create users with them,
# so they are only used by the integration tests:
PHOTO_ADMIN = "photo-admin"
ALBUM_ADMIN = "album-admin"
CONFIG_ADMIN = "config-admin"
STATUS_ADMIN = "status-admin"
PHOTO_SERVICE_ROLES = [PHOTO_ADMIN, ALBUM_ADMIN, CONFIG_ADMIN, STATUS_ADMIN]

# Roles that no longer exist, and must not give access:
REMOVED_ROLES = ["user-admin", "race-result", "race-office", "user"]

PHOTOS = {ADMIN, PHOTO_ADMIN}
ALBUMS = {ADMIN, ALBUM_ADMIN}
CONFIG = {ADMIN, CONFIG_ADMIN}
STATUS = {ADMIN, STATUS_ADMIN}

WRITE_ACCESS: dict[tuple[str, str], set[str]] = {
    ("POST", "/photos"): PHOTOS,
    ("PUT", "/photos/{photo_id}"): PHOTOS,
    ("DELETE", "/photos/{photo_id}"): PHOTOS,
    ("POST", "/service-instances"): PHOTOS,
    ("PUT", "/service-instances/{service_instance_id}"): PHOTOS,
    ("DELETE", "/service-instances/{service_instance_id}"): PHOTOS,
    ("POST", "/albums"): ALBUMS,
    ("PUT", "/albums/{album_id}"): ALBUMS,
    ("DELETE", "/albums/{album_id}"): ALBUMS,
    ("POST", "/config"): CONFIG,
    ("PUT", "/config"): CONFIG,
    ("DELETE", "/config/{config_id}"): CONFIG,
    ("POST", "/status"): STATUS,
    ("DELETE", "/status/{status_id}"): STATUS,
}


def access_cases(roles: list[str]) -> list[tuple[str, str, str, bool]]:
    """Return (method, path, role, allowed) for every write operation and role."""
    return [
        (method, path, role, role in allowed)
        for (method, path), allowed in WRITE_ACCESS.items()
        for role in roles
    ]
