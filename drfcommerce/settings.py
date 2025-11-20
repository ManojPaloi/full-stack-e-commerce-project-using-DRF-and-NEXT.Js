"""
=========================================
 Django Settings – Full CORS + CSRF FIXED
=========================================
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers, default_methods

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------
# SECURITY
# ---------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True

SERVER_IP = os.getenv("SERVER_IP", "13.49.70.126")

ALLOWED_HOSTS = [
    SERVER_IP,
    "next-e-commerce.onrender.com",
    "localhost",
    "127.0.0.1",
    "*",
]

# ---------------------------------------
# INSTALLED APPS
# ---------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

    # Local
    "accounts",
    "category",
    "banner",
    "products",
    "oders",
    "coupons",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
]

# ---------------------------------------
# MIDDLEWARE
# ---------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST BE FIRST
    "django.middleware.common.CommonMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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

# ---------------------------------------
# DATABASE
# ---------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------
# AUTH
# ---------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

# ---------------------------------------
# REST FRAMEWORK
# ---------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# ---------------------------------------
# SIMPLE JWT
# ---------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),

    # COOKIE SETTINGS FOR REFRESH TOKEN
    "AUTH_COOKIE": "refresh_token",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": False,       # EC2 IP → cannot use HTTPS
    "AUTH_COOKIE_SAMESITE": "Lax",
}

# ---------------------------------------
# STATIC / MEDIA
# ---------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------
# =======================
#  CORS + CSRF FIX (FINAL)
# =======================
# ---------------------------------------

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://next-e-commerce.onrender.com",
    f"http://{SERVER_IP}",       # EC2 SERVER
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "https://next-e-commerce.onrender.com",
    f"http://{SERVER_IP}",
]

CORS_ALLOW_METHODS = list(default_methods)
CORS_ALLOW_HEADERS = list(default_headers) + [
    "content-type",
    "x-csrftoken",
    "authorization",
]

# ---------------------------------------
# NO HTTPS because server uses IP
# ---------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ---------------------------------------
# EMAIL (GMAIL)
# ---------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
