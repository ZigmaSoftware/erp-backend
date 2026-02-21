from pathlib import Path
import os
import sys

# --------------------------------------------------
# BASE DIR
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# __file__ = /home/sathya/erp/erp-final-backend/auth_service/config/settings/base.py
# .parent = /home/sathya/erp/erp-final-backend/auth_service/config/settings/
# .parent = /home/sathya/erp/erp-final-backend/auth_service/config/
# .parent = /home/sathya/erp/erp-final-backend/auth_service/
# BASE_DIR = /home/sathya/erp/erp-final-backend/auth_service/

# --------------------------------------------------
# COMMON LIB PATH (auto-detect relative to project)
# --------------------------------------------------
PROJECT_ROOT = BASE_DIR.parent
# .parent = /home/sathya/erp/erp-final-backend/
# PROJECT_ROOT = /home/sathya/erp/erp-final-backend/

COMMON_LIB = PROJECT_ROOT / "common_lib"
# COMMON_LIB = /home/sathya/erp/erp-final-backend/common_lib/

if str(COMMON_LIB) not in sys.path:
    sys.path.insert(0, str(COMMON_LIB))

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0"
]

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    "corsheaders",  # REQUIRED FOR CORS

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_yasg",
    "apps.authentication",
]

# --------------------------------------------------
# MIDDLEWARE (ORDER IS CRITICAL)
# --------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST BE FIRST
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    # KEEP ENABLED – SAFE FOR JWT (not cookies)
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URL / WSGI
# --------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --------------------------------------------------
# DATABASE (DEV EXAMPLE)
# --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "CONN_MAX_AGE": 60,
    }
}

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# PASSWORD HASHERS
# --------------------------------------------------
PASSWORD_HASHERS = [
    "config.hashers.PBKDF2SHA256IterationsHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        # add JWT auth class if implemented
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# --------------------------------------------------
# JWT SETTINGS
# --------------------------------------------------
JWT_SETTINGS = {
    "ALGORITHM": os.getenv("JWT_ALGORITHM", "RS256"),
    "ISSUER": os.getenv("JWT_ISSUER", "auth_service"),
    "ACCESS_TOKEN_LIFETIME": int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", 3600)),
    "REFRESH_TOKEN_LIFETIME": int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", 604800)),
}

# --------------------------------------------------
# CORS SETTINGS (React / Vite)
# --------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# DO NOT enable unless using cookies
# CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------
# CSRF (Frontend trusted)
# --------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------
STATIC_URL = "/static/"

# --------------------------------------------------
# DEFAULT FIELD
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"