"""
Production settings for Auth Service.

STRICTLY production-only.
"""

from .base import *
import os


# ------------------------------------------------------------
# Core flags
# ------------------------------------------------------------
DEBUG = False


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise RuntimeError("ALLOWED_HOSTS must be set in production")


# ------------------------------------------------------------
# Database (MariaDB / MySQL)
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("PROD_DB_NAME"),
        "USER": os.getenv("PROD_DB_USER"),
        "PASSWORD": os.getenv("PROD_DB_PASSWORD"),
        "HOST": os.getenv("PROD_DB_HOST"),
        "PORT": os.getenv("PROD_DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

if not DATABASES["default"]["NAME"]:
    raise RuntimeError("Production database configuration missing")


# ------------------------------------------------------------
# Security hardening
# ------------------------------------------------------------
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


# ------------------------------------------------------------
# CORS (strict)
# ------------------------------------------------------------
INSTALLED_APPS += [
    "corsheaders",
]

MIDDLEWARE.insert(2, "corsheaders.middleware.CorsMiddleware")

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")


# ------------------------------------------------------------
# CSRF
# ------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")


# ------------------------------------------------------------
# JWT keys (MUST be provided)
# ------------------------------------------------------------
JWT_PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH")
JWT_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH")

if not JWT_PRIVATE_KEY_PATH or not JWT_PUBLIC_KEY_PATH:
    raise RuntimeError("JWT key paths must be set in production")


# ------------------------------------------------------------
# Logging (structured, production-safe)
# ------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
