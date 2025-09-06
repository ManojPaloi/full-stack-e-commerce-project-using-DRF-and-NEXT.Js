from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Local dev: don’t enforce HTTPS-only cookies
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
