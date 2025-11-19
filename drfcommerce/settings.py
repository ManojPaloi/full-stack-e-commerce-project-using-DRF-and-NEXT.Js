"""
=========================================
 Django Settings for DRF E-Commerce API
 - CORS & CSRF fixes for Next.js frontend (preflight OPTIONS)
 - Secure cookie + JWT settings
 - Minimal, documented, production-aware settings
=========================================
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# ---------------------------------------------------
# BASE DIR & ENV
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(str(BASE_DIR / ".env"))

# ---------------------------------------------------
# SECURITY
# ---------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Hosts: keep your IP + domain
ALLOWED_HOSTS = [
    "13.49.70.126",
    "next-e-commerce.onrender.com",
    "*",
]

# ---------------------------------------------------
# INSTALLED APPS
# ---------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local
    "accounts",
    "category",
    "banner",
    "products",
    "oders",
    "coupons",

    # Third-party
    "corsheaders",
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
]

# ---------------------------------------------------
# MIDDLEWARE
# Important: corsheaders.middleware.CorsMiddleware must be high (first)
# ---------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be first so it handles OPTIONS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------
# URL & TEMPLATES
# ---------------------------------------------------
ROOT_URLCONF = "drfcommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "drfcommerce.wsgi.application"

# ---------------------------------------------------
# DATABASE
# ---------------------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
        }
    }

# ---------------------------------------------------
# AUTH & PASSWORD VALIDATION
# ---------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------
# STATIC & MEDIA
# ---------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------
# AUTH USER MODEL & BACKENDS
# ---------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ---------------------------------------------------
# REST FRAMEWORK
# ---------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    # Optionally add renderers if needed:
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# ---------------------------------------------------
# SIMPLE JWT
# ---------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MIN", "5"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),

    # Cookie configuration (used by your views)
    "AUTH_COOKIE": "refresh_token",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": not DEBUG,
    "AUTH_COOKIE_SAMESITE": "None" if not DEBUG else "Lax",
}

# ---------------------------------------------------
# CORS & CSRF (Fixed for preflight & Next.js)
# ---------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

SERVER_IP = os.getenv("SERVER_IP", "13.49.70.126")

# Keep exact origins only — browsers require exact match for credentials
CORS_ALLOWED_ORIGINS = [
    f"https://{SERVER_IP}",
    f"http://{SERVER_IP}",
    "https://next-e-commerce.onrender.com",
    "http://localhost:3000",
    "https://localhost:3000",
]

# CSRF trusted origins (exact)
CSRF_TRUSTED_ORIGINS = [
    f"https://{SERVER_IP}",
    "https://next-e-commerce.onrender.com",
]

# Allow preflight methods
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# Ensure content-type and commonly requested headers are allowed in preflight
CORS_ALLOW_HEADERS = list(default_headers) + [
    "content-type",
    "authorization",
    "x-csrftoken",
    "x-requested-with",
]

# Optional: If your frontend might use uppercase header names, default_headers already covers many cases.
# But above list includes explicit commonly used ones.

# ---------------------------------------------------
# SECURITY SETTINGS (keep secure in production)
# ---------------------------------------------------
# When serving via IP + HTTPS (ALB / proxy), avoid forcing Django to redirect
SECURE_SSL_REDIRECT = False

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# ---------------------------------------------------
# EMAIL
# ---------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# ---------------------------------------------------
# JAZZMIN (optional UI tweaks)
# ---------------------------------------------------
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "cyborg",
    "navbar": "navbar-dark bg-gradient-primary",
    "sidebar": "sidebar-dark-primary elevation-4",
    "brand_colour": "navbar-primary",
    "accent": "accent-info",
    "sidebar_nav_small_text": True,
    "footer_fixed": True,
    "navbar_fixed": True,
}

# ---------------------------------------------------
# LOGGING FOR DEBUGGING (remove or lower level in prod)
# ---------------------------------------------------
import logging
logger = logging.getLogger("django")

logger.error("=== Django settings debug start ===")
try:
    logger.error("CORS_ALLOWED_ORIGINS => %s", CORS_ALLOWED_ORIGINS)
    logger.error("CSRF_TRUSTED_ORIGINS => %s", CSRF_TRUSTED_ORIGINS)
    logger.error("DEBUG => %s", DEBUG)
    logger.error("ALLOWED_HOSTS => %s", ALLOWED_HOSTS)
except Exception as e:
    logger.error("Error printing settings debug: %s", e)
logger.error("=== Django settings debug end ===")
