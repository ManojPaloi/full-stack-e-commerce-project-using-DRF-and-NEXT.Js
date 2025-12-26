import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# -------------------------------------------------------------------
# Base dir & load environment variables (explicit path)
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
# Ensure we load the .env file from the project BASE_DIR so systemd/gunicorn picks it up
load_dotenv(str(BASE_DIR / ".env"))

# -------------------------------------------------------------------
# Security & Debug
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]
DEBUG = False
ALLOWED_HOSTS = ['13.51.195.39', "next-e-commerce.onrender.com"]

# -------------------------------------------------------------------
# Installed Apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "accounts", "category", "banner", "products", "oders", "coupons",
    # Third-party apps
    "rest_framework", "django_filters", "rest_framework_simplejwt", "corsheaders",
]

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
# Password validation
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
# Static & Media
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
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
# Simple JWT
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
    "AUTH_COOKIE_SECURE": not DEBUG,
    "AUTH_COOKIE_SAMESITE": "None" if not DEBUG else "Lax",
}

# -------------------------------------------------------------------
# CORS & CSRF
# -------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']


SERVER_IP = os.getenv("SERVER_IP", "13.49.70.126")

CORS_ALLOWED_ORIGINS = [
    f"https://{SERVER_IP}",
    f"http://{SERVER_IP}",
    "http://localhost:3000",
    "https://localhost:3000",
    "https://next-e-commerce.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    f"https://{SERVER_IP}",
    "https://next-e-commerce.onrender.com",
]

CORS_ALLOW_ALL_ORIGINS = False

# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
SECURE_SSL_REDIRECT = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

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

# --- DEBUG LOG (remove after debugging) -----------------------
# These logs will show up in gunicorn/journalctl to confirm the loaded values.
# Remove this block after you confirm the CORS/CSRF values are correct.
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
# --------------------------------------------------------------
