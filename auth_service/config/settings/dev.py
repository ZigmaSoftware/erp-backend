from .base import *
import os

DEBUG = True

SECRET_KEY = "dev-only-secret"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "auth_service_db",
        "USER": "root",
        "PASSWORD": "Su$i0410",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

ALLOWED_HOSTS = ["*"]

# JWT keys (development defaults)
JWT_PRIVATE_KEY_PATH = os.getenv(
    "JWT_PRIVATE_KEY_PATH",
    BASE_DIR / "keys/dev_private.pem",
)

JWT_PUBLIC_KEY_PATH = os.getenv(
    "JWT_PUBLIC_KEY_PATH",
    BASE_DIR / "keys/dev_public.pem",
)

