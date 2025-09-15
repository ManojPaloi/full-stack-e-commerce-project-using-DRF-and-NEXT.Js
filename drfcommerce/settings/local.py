from .base import *

# ------------------------
# Debug Mode
# ------------------------
DEBUG = True  # ✅ Enable debug locally only

# ------------------------
# Database
# ------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # ✅ Use SQLite for local dev
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------
# Allowed Hosts
# ------------------------
# Add your Render domain for testing remote frontend integration
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "e-commerce-api-a5il.onrender.com",  # ✅ Allow your hosted backend to work with the local frontend
]

# ------------------------
# Security (Local Dev)
# ------------------------
# Disable HTTPS-only settings for local testing
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# ------------------------
# CORS Settings
# ------------------------
CORS_ALLOW_ALL_ORIGINS = True  # ✅ Convenient for dev
# Optionally restrict to your dev frontend URLs:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:5173",
# ]

# ------------------------
# CSRF Trusted Origins
# ------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "https://e-commerce-api-a5il.onrender.com",  # ✅ Add your Render domain for production-like testing
]
