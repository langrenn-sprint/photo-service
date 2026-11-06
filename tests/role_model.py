"""The role model for photo-service, shared by the integration and contract tests.

See langrenn-sprint/event-service-gui#215. All GET operations are open. Every
write operation is listed here with the roles that may call it: admin, and
result-admin for photos.
"""

ADMIN = "admin"
EVENT_ADMIN = "event-admin"
RESULT_ADMIN = "result-admin"
CONTESTANT_ADMIN = "contestant-admin"
# The roles user-service creates users with:
ROLES = [ADMIN, EVENT_ADMIN, RESULT_ADMIN, CONTESTANT_ADMIN]

# Roles that no longer exist, and must not give access. photo-service had its
# own roles (photo-admin etc.), but user-service could not create users with them:
REMOVED_ROLES = [
    "user-admin",
    "race-result",
    "race-office",
    "user",
    "photo-admin",
    "album-admin",
    "config-admin",
    "status-admin",
]

# result-admin may edit photos on raceday; everything else is admin-only:
PHOTOS = {ADMIN, RESULT_ADMIN}
ADMIN_ONLY = {ADMIN}

WRITE_ACCESS: dict[tuple[str, str], set[str]] = {
    ("POST", "/photos"): PHOTOS,
    ("PUT", "/photos/{photo_id}"): PHOTOS,
    ("DELETE", "/photos/{photo_id}"): PHOTOS,
    ("POST", "/service-instances"): ADMIN_ONLY,
    ("PUT", "/service-instances/{service_instance_id}"): ADMIN_ONLY,
    ("DELETE", "/service-instances/{service_instance_id}"): ADMIN_ONLY,
    ("POST", "/albums"): ADMIN_ONLY,
    ("PUT", "/albums/{album_id}"): ADMIN_ONLY,
    ("DELETE", "/albums/{album_id}"): ADMIN_ONLY,
    ("POST", "/config"): ADMIN_ONLY,
    ("PUT", "/config"): ADMIN_ONLY,
    ("DELETE", "/config/{config_id}"): ADMIN_ONLY,
    ("POST", "/status"): ADMIN_ONLY,
    ("DELETE", "/status/{status_id}"): ADMIN_ONLY,
}


def access_cases(roles: list[str]) -> list[tuple[str, str, str, bool]]:
    """Return (method, path, role, allowed) for every write operation and role."""
    return [
        (method, path, role, role in allowed)
        for (method, path), allowed in WRITE_ACCESS.items()
        for role in roles
    ]
