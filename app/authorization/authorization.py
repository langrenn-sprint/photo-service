"""Authorization dependencies for FastAPI routes."""

import logging
import os
from dataclasses import dataclass
from enum import StrEnum
from http import HTTPStatus
from typing import Annotated, Any

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger("uvicorn.error")


class TokenError(Exception):
    """Base token error."""


class TokenMissingError(TokenError):
    """Token missing error."""

    @classmethod
    def missing_bearer_token(cls) -> "TokenMissingError":
        """Create error for missing or malformed bearer token header."""
        return cls("Authorization header missing or not a Bearer token")


class TokenValidationError(TokenError):
    """Token validation error."""

    @classmethod
    def expired_token(cls) -> "TokenValidationError":
        """Create error for expired JWT token."""
        return cls("Token has expired")

    @classmethod
    def invalid_signature(cls) -> "TokenValidationError":
        """Create error for invalid JWT signature."""
        return cls("Token signature is invalid")

    @classmethod
    def decode_error(cls) -> "TokenValidationError":
        """Create error for undecodable JWT token."""
        return cls("Token could not be decoded")

    @classmethod
    def missing_required_claim(cls, error: Exception) -> "TokenValidationError":
        """Create error for missing required JWT claim."""
        return cls(f"Token is missing required claim: {error!s}")

    @classmethod
    def invalid_token(cls) -> "TokenValidationError":
        """Create error for other invalid JWT token cases."""
        return cls("Token is invalid")

    @classmethod
    def missing_expected_claim(cls, error: Exception) -> "TokenValidationError":
        """Create error for missing token claims required by this service."""
        return cls(f"Missing expected claim in token: {error}")


class APIConfigurationError(TokenError):
    """API configuration error."""


class APIKeyError(TokenError):
    """API key error."""


class TokenValidator:
    """Validates JWT tokens."""

    def validate_token(self, token: str) -> dict[str, Any]:  # pragma: no cover
        """Validate and decode a JWT token."""
        try:
            secret_key = os.getenv("JWT_SECRET")
            if not secret_key:
                msg = "JWT secret key is not configured"
                logger.error(msg)
                raise APIConfigurationError(msg)
            return jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            raise TokenValidationError.expired_token() from e
        except jwt.InvalidSignatureError as e:
            raise TokenValidationError.invalid_signature() from e
        except jwt.DecodeError as e:
            raise TokenValidationError.decode_error() from e
        except jwt.MissingRequiredClaimError as e:
            raise TokenValidationError.missing_required_claim(e) from e
        except jwt.InvalidTokenError as e:
            raise TokenValidationError.invalid_token() from e


@dataclass
class TokenData:
    """Data extracted from a JWT token."""

    sub: str
    name: str
    roles: list[str]
    exp: int


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_token(
    http_credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> TokenData:  # pragma: no cover
    """Extract and validate JWT token from request."""
    token = None
    if http_credentials and http_credentials.scheme.lower() == "bearer":
        token = http_credentials.credentials

    if not token:
        raise TokenMissingError.missing_bearer_token()

    validator = TokenValidator()
    payload = validator.validate_token(token)

    try:
        sub = payload["username"]
        name = payload.get("name", "")
        role = payload.get("role", "")
        exp = payload["exp"]
        return TokenData(sub=sub, name=name, roles=[role], exp=exp)
    except KeyError as e:
        raise TokenValidationError.missing_expected_claim(e) from e


class UserRole(StrEnum):
    """Enum of user roles."""

    Admin = "admin"
    ResultAdmin = "result-admin"


class RoleChecker:
    """Dependency that checks if the user has the required role."""

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        """Initialize with allowed roles."""
        self.allowed_roles = allowed_roles

    async def __call__(
        self, token_data: Annotated[TokenData, Depends(get_current_token)]
    ) -> None:
        """Check if the user has an allowed role."""
        user_roles = token_data.roles
        for role in user_roles:
            if role in [allowed_role.value for allowed_role in self.allowed_roles]:
                return
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Operation forbidden"
        )


def require_roles(*roles: UserRole) -> Any:
    """Dependency that allows only users with one of the given roles.

    The roles are also given as scopes on the security requirement, so the
    OpenAPI document lists them for the bearer scheme (allowed for non-OAuth2
    schemes in OpenAPI 3.1). See document_roles for the description text.
    """
    return Security(RoleChecker(list(roles)), scopes=[role.value for role in roles])


def document_roles(api: FastAPI) -> None:
    """Show the allowed roles for each operation in the OpenAPI document.

    For every operation protected by require_roles, the roles are added to
    the description, and the 401 and 403 responses are documented.
    """
    generate_openapi = api.openapi

    def openapi() -> dict[str, Any]:
        if api.openapi_schema:
            return api.openapi_schema
        schema = generate_openapi()
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                roles = list(
                    dict.fromkeys(
                        role
                        for requirement in operation.get("security", [])
                        for scope in requirement.values()
                        for role in scope
                    )
                )
                if not roles:
                    continue
                roles_text = "**Roles:** " + ", ".join(f"`{r}`" for r in roles)
                description = operation.get("description")
                operation["description"] = (
                    f"{description}\n\n{roles_text}" if description else roles_text
                )
                responses = operation.setdefault("responses", {})
                responses.setdefault("401", {"description": "Missing or invalid token"})
                responses.setdefault(
                    "403",
                    {
                        "description": "Operation forbidden: requires one of the roles "
                        + ", ".join(roles)
                    },
                )
        return schema

    api.openapi = openapi  # ty: ignore[invalid-assignment]
