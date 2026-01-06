import jwt
from pathlib import Path
from django.conf import settings
from jwt import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)


class JWTDecodeError(Exception):
    """Base JWT decode error."""


class JWTExpiredError(JWTDecodeError):
    """Token expired."""


class JWTInvalidError(JWTDecodeError):
    """Token invalid or tampered."""


def _load_public_key() -> str:
    """
    Load RSA public key used for verifying JWTs.
    """
    return Path(settings.JWT_PUBLIC_KEY_PATH).read_text()


def decode_token(token: str, expected_type: str | None = None) -> dict:
    """
    Decode and validate a JWT.

    :param token: JWT string
    :param expected_type: 'access' or 'refresh' (optional)
    :return: decoded payload
    :raises: JWTExpiredError, JWTInvalidError
    """
    try:
        payload = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_SETTINGS["ALGORITHM"]],
            audience=None,
            issuer=settings.JWT_SETTINGS["ISSUER"],
        )

        if expected_type and payload.get("type") != expected_type:
            raise JWTInvalidError("Invalid token type")

        return payload

    except ExpiredSignatureError:
        raise JWTExpiredError("Token expired")

    except (InvalidSignatureError, InvalidTokenError):
        raise JWTInvalidError("Invalid token")
