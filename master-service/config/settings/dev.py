from .base import *

DEBUG = True

SECRET_KEY = "dev-only-secret"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "master_service_db",
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
