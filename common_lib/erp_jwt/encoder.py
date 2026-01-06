import time
import jwt
from pathlib import Path
from django.conf import settings


def _load_private_key() -> str:
    """
    Load RSA private key used for signing JWTs.
    """
    return Path(settings.JWT_PRIVATE_KEY_PATH).read_text()


def generate_access_token(user) -> str:
    """
    Generate short-lived access token.
    """
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "groups": list(user.groups.values_list("name", flat=True)),
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_SETTINGS["ACCESS_TOKEN_LIFETIME"],
        "iss": settings.JWT_SETTINGS["ISSUER"],
        "type": "access",
    }

    return jwt.encode(
        payload,
        _load_private_key(),
        algorithm=settings.JWT_SETTINGS["ALGORITHM"],
    )


def generate_refresh_token(user) -> str:
    """
    Generate long-lived refresh token.
    """
    payload = {
        "sub": str(user.id),
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_SETTINGS["REFRESH_TOKEN_LIFETIME"],
        "iss": settings.JWT_SETTINGS["ISSUER"],
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        _load_private_key(),
        algorithm=settings.JWT_SETTINGS["ALGORITHM"],
    )
