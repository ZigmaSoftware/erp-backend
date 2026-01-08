"""
JWT Decoder Utility
-------------------
Used by API Gateway and other services to validate RS256 JWTs
issued by auth_service.

This module is production-safe:
- No hardcoded paths
- Fails cleanly (401-style errors, no 500s)
- Enforces issuer and algorithm
"""

import jwt
from pathlib import Path
from django.conf import settings
from jwt import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)


# ============================================================
# Custom Exceptions (domain-level, not PyJWT-leakage)
# ============================================================

class JWTDecodeError(Exception):
    """Base JWT decode error."""


class JWTExpiredError(JWTDecodeError):
    """Token expired."""


class JWTInvalidError(JWTDecodeError):
    """Token invalid, tampered, or misconfigured."""


# ============================================================
# Internal helpers
# ============================================================

def _load_public_key() -> str:
    """
    Load RSA public key used for verifying JWTs.
    Converts filesystem / config issues into auth failures
    instead of crashing the request pipeline.
    """
    key_path = Path(settings.JWT_PUBLIC_KEY_PATH)

    if not key_path.exists():
        raise JWTInvalidError(
            f"JWT public key not found at {key_path}"
        )

    return key_path.read_text()


# ============================================================
# Public API
# ============================================================

def decode_token(token: str, expected_type: str | None = None) -> dict:
    """
    Decode and validate a JWT.

    :param token: JWT string (Bearer token without prefix)
    :param expected_type: 'access' or 'refresh' (optional)
    :return: decoded JWT payload
    :raises: JWTExpiredError, JWTInvalidError
    """

    algorithm = settings.JWT_SETTINGS.get("ALGORITHM")
    issuer = settings.JWT_SETTINGS.get("ISSUER")

    # Defensive guard: never allow symmetric algorithms here
    if not algorithm or algorithm.startswith("HS"):
        raise RuntimeError(
            "Invalid JWT algorithm configuration; RS* required"
        )

    try:
        payload = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[algorithm],
            issuer=issuer,
            options={
                "require": ["exp", "iat", "iss"],
                "verify_aud": False,  # enable later if aud is introduced
            },
        )

        # Enforce token type if requested
        if expected_type and payload.get("type") != expected_type:
            raise JWTInvalidError("Invalid token type")

        return payload

    except ExpiredSignatureError:
        raise JWTExpiredError("Token expired")

    except (InvalidSignatureError, InvalidTokenError):
        raise JWTInvalidError("Invalid token")
