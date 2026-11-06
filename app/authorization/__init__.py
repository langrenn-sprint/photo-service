"""Package for authorization."""

from .authorization import (
    APIConfigurationError,
    APIKeyError,
    RoleChecker,
    TokenData,
    TokenError,
    TokenMissingError,
    TokenValidationError,
    TokenValidator,
    UserRole,
    document_roles,
    get_current_token,
    require_roles,
)

__all__ = [
    "APIConfigurationError",
    "APIKeyError",
    "RoleChecker",
    "TokenData",
    "TokenError",
    "TokenMissingError",
    "TokenValidationError",
    "TokenValidator",
    "UserRole",
    "document_roles",
    "get_current_token",
    "require_roles",
]
