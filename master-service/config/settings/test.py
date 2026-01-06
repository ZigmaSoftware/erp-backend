from .base import *

# Tests must be deterministic and isolated
DEBUG = False

SECRET_KEY = "test-only-secret-key"

ALLOWED_HOSTS = ["testserver"]

# Use a separate TEST database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "master_service_test_db",
        "USER": "master_test_user",
        "PASSWORD": "master_test_pass",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "TEST": {
            "NAME": "master_service_test_db",
        },
    }
}

# Speed up tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable unnecessary middleware side effects
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable migrations for faster test runs (recommended for large ERP)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Make time-based tests predictable
USE_TZ = True
TIME_ZONE = "UTC"
