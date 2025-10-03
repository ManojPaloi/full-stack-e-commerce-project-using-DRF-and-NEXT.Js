from .base import *

DEBUG = True

ALLOWED_HOSTS = ["13.49.70.126", "127.0.0.1", "localhost"]

# Enable CORS for development
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://13.49.70.126:8000",
]
