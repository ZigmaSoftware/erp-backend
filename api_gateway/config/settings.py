"""
Django settings for API Gateway project.
"""

from pathlib import Path
import os
import sys

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
COMMON_LIB = PROJECT_ROOT / "common_lib"

if str(COMMON_LIB) not in sys.path:
    sys.path.insert(0, str(COMMON_LIB))

# --------------------------------------------------
# Core Settings
# --------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-gateway-key-change-in-production")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# --------------------------------------------------
# Service URLs
#
# One entry per backend microservice. The key is the URL slug used
# by both the gateway route (gateway/urls.py) and the frontend
# (erp-frontend src/helpers/admin/endpoints.ts) - e.g. requests to
# /api/<key>/... are proxied to SERVICE_URLS[<key>].
#
# To add a new service: add one line here (backed by its own env
# var so the port can be changed without touching code), then one
# path() line in gateway/urls.py. No new proxy class needed.
# --------------------------------------------------
SERVICE_URLS = {
    "auth-service": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001"),
    "master-service": os.getenv("MASTER_SERVICE_URL", "http://127.0.0.1:8002"),
    "sales-service": os.getenv("SALES_SERVICE_URL", "http://127.0.0.1:8003"),
}

# Back-compat aliases (some code may still read these directly).
AUTH_SERVICE_URL = SERVICE_URLS["auth-service"]
MASTER_SERVICE_URL = SERVICE_URLS["master-service"]
SALES_SERVICE_URL = SERVICE_URLS["sales-service"]

PROXY_TIMEOUT = int(os.getenv("PROXY_TIMEOUT", "10"))

# --------------------------------------------------
# JWT Configuration
# --------------------------------------------------
JWT_SETTINGS = {
    "ALGORITHM": os.getenv("JWT_ALGORITHM", "RS256"),
    "ISSUER": os.getenv("JWT_ISSUER", "auth_service"),
}

JWT_PUBLIC_KEY_PATH = os.getenv(
    "JWT_PUBLIC_KEY_PATH",
    str(PROJECT_ROOT / "auth_service" / "keys" / "dev_public.pem"),
)

# --------------------------------------------------
# Applications
# --------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "corsheaders",
    "gateway",
]

# --------------------------------------------------
# Middleware
# --------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "gateway.middleware.jwt_auth.JWTAuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8001,http://127.0.0.1:8001,http://0.0.0.0:8001,http://0.0.0.0:8000"
).split(",")

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ["Authorization", "X-User-Id", "X-Username", "X-Groups"]
CORS_EXPOSE_HEADERS = ["Authorization", "X-User-Id", "X-Username", "X-Groups"]
CORS_ALLOW_CREDENTIALS = False
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# --------------------------------------------------
# URLs / WSGI
# --------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# --------------------------------------------------
# Static Files
# --------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------
# Logging
# --------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
    "loggers": {
        "gateway": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "requests": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}