from pathlib import Path
import os
import sys

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
# __file__ = /home/sathya/erp/erp-final-backend/api_gateway/config/settings.py
# .parent = /home/sathya/erp/erp-final-backend/api_gateway/config/
# .parent = /home/sathya/erp/erp-final-backend/api_gateway/
# BASE_DIR = /home/sathya/erp/erp-final-backend/api_gateway/

PROJECT_ROOT = BASE_DIR.parent
# .parent = /home/sathya/erp/erp-final-backend/
# PROJECT_ROOT = /home/sathya/erp/erp-final-backend/

COMMON_LIB = PROJECT_ROOT / "common_lib"
# COMMON_LIB = /home/sathya/erp/erp-final-backend/common_lib/

if str(COMMON_LIB) not in sys.path:
    sys.path.insert(0, str(COMMON_LIB))


# --------------------------------------------------
# Core
# --------------------------------------------------
SECRET_KEY = "dev-only-gateway-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]  # tighten later


# --------------------------------------------------
# JWT config (shared contract with auth_service)
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
# Middleware (JWT first, always)
# --------------------------------------------------
MIDDLEWARE = [
    # CORS middleware should be as high as possible so preflight requests are handled
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "gateway.middleware.jwt_auth.JWTAuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# CORS: allow auth service in dev so the login page can call gateway with Authorization header
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8001",
    "http://localhost:8001",
    "http://0.0.0.0:8001",
    "http://0.0.0.0:8000",
    # Allow frontend dev server origins
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ["Authorization"]
CORS_EXPOSE_HEADERS = ["Authorization"]
CORS_ALLOW_CREDENTIALS = False


# --------------------------------------------------
# URLs / WSGI
# --------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------
# Database (rarely used, but Django wants one)
# --------------------------------------------------
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# --------------------------------------------------
# Static (optional)
# --------------------------------------------------
STATIC_URL = "static/"
