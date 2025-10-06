"""
Django settings for drfcommerce project.
Unified from base.py, local.py, and production.py
"""

import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# Security & Debug
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
DEBUG = False  # Always False in production
ALLOWED_HOSTS = [os.getenv("SERVER_IP", "13.60.200.77")]  # Replace with your EC2 public IP or domain


# Detect if running manage.py runserver
IS_RUNSERVER = "runserver" in sys.argv

# -------------------------------------------------------------------
# Installed Apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Admin
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "accounts",
    "category",
    "banner",
    "products",
    "oders",
    "coupons",

    # Third-party apps
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "corsheaders",
]

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------------------
# URL & Templates
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Password Validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static & Media (production-ready)
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # Nginx will serve static files from here

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"          # Nginx will serve uploaded media from here

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# -------------------------------------------------------------------
# Simple JWT (production-ready)
# -------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MIN", "5"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_COOKIE": "refresh_token",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": True,             # Force secure cookie for HTTPS
    "AUTH_COOKIE_SAMESITE": "None",         # Required for cross-site usage over HTTPS
}

# -------------------------------------------------------------------
# CORS & CSRF
# -------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG or IS_RUNSERVER

CORS_ALLOW_ALL_ORIGINS = False  # Disable wildcard in production

CORS_ALLOWED_ORIGINS = [
    f"https://{os.getenv('SERVER_IP', '13.60.200.77')}",  # Backend domain/IP
]

CSRF_TRUSTED_ORIGINS = [
    f"https://{os.getenv('SERVER_IP', '13.60.200.77')}",
]


CORS_ALLOW_HEADERS = list(default_headers) + ["x-csrftoken"]

# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# -------------------------------------------------------------------
# Email
# -------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# -------------------------------------------------------------------
# Jazzmin Admin UI Tweaks
# -------------------------------------------------------------------
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "cyborg",
    "navbar": "navbar-dark bg-gradient-primary",
    "sidebar": "sidebar-dark-primary elevation-4",
    "brand_colour": "navbar-primary",
    "accent": "accent-info",
    "button_classes": {
        "primary": "btn btn-primary btn-lg rounded-pill shadow",
        "secondary": "btn btn-outline-secondary rounded-pill",
    },
    "sidebar_nav_small_text": True,
    "footer_fixed": True,
    "navbar_fixed": True,
}
