from .base import *
import os

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Local development: disable HTTPS-only settings
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Read from environment variable or fallback to list of allowed hosts
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "13.60.196.170"]


# Optional: print for debugging
print("ALLOWED_HOSTS:", ALLOWED_HOSTS)
