from .base import *

DEBUG = False

SECRET_KEY = "MOVE_TO_ENV_VARIABLE"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "sales_service_db",
        "USER": "sales_user",
        "PASSWORD": "STRONG_PASSWORD",
        "HOST": "mariadb-master",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

ALLOWED_HOSTS = ["api.yourdomain.com"]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
