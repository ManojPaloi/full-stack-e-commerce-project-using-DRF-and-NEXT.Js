import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# -------------------------------------------------------------------
# ✅ Load environment variables (from .env file for secrets)
# -------------------------------------------------------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")  # Secret key for Django
DEBUG = os.getenv("DEBUG", "True") == "True"  # Toggle debugging for development

# Hosts allowed to serve the app
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# -------------------------------------------------------------------
# ✅ Installed Apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Admin UI customization
    "jazzmin",

    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps (your project modules)
    "accounts",
    "category",
    "banner",
    "products",
    "oders",
    "coupons",

    # Third-party apps
    "rest_framework",           # Django REST Framework
    "django_filters",           # Filtering support for DRF
    "rest_framework_simplejwt", # JWT authentication
    "corsheaders",              # CORS support for cross-origin requests
]

# -------------------------------------------------------------------
# ✅ Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ⚡ Must come first for CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection for POST requests
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------------------
# 🌐 CORS Settings for Frontend <-> Backend Communication
# -------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type",
    "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with",
]

# ✅ Trust frontend origins for CSRF cookies
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# -------------------------------------------------------------------
# 📂 URL and WSGI
# -------------------------------------------------------------------
ROOT_URLCONF = "drfcommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Add template directories here if needed
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
# 🗄 Database (SQLite for dev, replace for production)
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------------------
# 🔒 Password Validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# 🌍 Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# 🖼 Static & Media Files
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# 👤 Custom User Model
# -------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

# Allow login with either email or username
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# -------------------------------------------------------------------
# 🔗 Django REST Framework Config
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",    # Your custom JWT auth
        "rest_framework_simplejwt.authentication.JWTAuthentication", # DRF SimpleJWT
        "rest_framework.authentication.SessionAuthentication",        # Browsable API
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
}

# -------------------------------------------------------------------
# 🔑 SimpleJWT Configuration with Cookie Support
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 🔑 SimpleJWT Configuration with Cookie Support
# -------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),

    # Cookie settings for storing refresh tokens securely
    "AUTH_COOKIE": "refresh_token",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": True,      # ✅ Add/Update here for local dev
    "AUTH_COOKIE_SAMESITE": "None",    # ✅ Add/Update here for local dev
}


# -------------------------------------------------------------------
# 📧 Email Configuration (OTP / Password Reset)
# -------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")           # Your email address
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")   # App password or email password
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)




# -------------------------------------------------------------------
# Jazzmin UI Tweaks (Responsive + Modern Look)
# -------------------------------------------------------------------
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",                     # Base theme
    "dark_mode_theme": "cyborg",           # Extra dark mode option
    "navbar": "navbar-dark bg-gradient-primary",  
    "sidebar": "sidebar-dark-primary elevation-4",
    "brand_colour": "navbar-primary",
    "accent": "accent-info",
    "button_classes": {
        "primary": "btn btn-primary btn-lg rounded-pill shadow",
        "secondary": "btn btn-outline-secondary rounded-pill",
    },
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "footer_fixed": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "actions_sticky_top": True,
    "show_ui_builder": False,
}






