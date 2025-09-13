import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url


# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ['*']




# -------------------------------------------------------------------
# Installed apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # "grappelli",
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


    # Third-party
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    # 'rest_framework_simplejwt.token_blacklist',
    "corsheaders",
 
]

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # must be high
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]





CORS_ALLOW_ALL_ORIGINS = True  # optional, currently set

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]









# -------------------------------------------------------------------
# URL / WSGI
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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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
# Static & Media files
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# Custom User Model
# -------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",  # custom backend
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    # 🔑 Authentication backends
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",  # ✅ Custom JWT blocklist
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # 🔒 Default permissions
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # ✅ Safer default for development
    ],

    # 🖼 Renderers for API responses
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],

    # 🔍 Filtering support (required for django-filter)
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
}






# -------------------------------------------------------------------
# JWT Settings
# -------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),  
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
}

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://mern-ecommerce-woad-three.vercel.app"
).split(",")

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CSRF_TRUSTED_ORIGINS = [
    "https://mern-ecommerce-woad-three.vercel.app",
    "https://your-backend.onrender.com",
]

# -------------------------------------------------------------------
# Email (for OTP / Forgot Password)
# -------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)




# -------------------------------------------------------------------
# Jazzmin Admin Theme (Enhanced)
# -------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "MyStore Admin",
    "site_header": "MyStore Dashboard",
    "site_brand": "MyStore",
    "welcome_sign": "Welcome back 👋",
    "copyright": "MyStore © 2025",

    # Logos
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "login_logo_dark": "images/logo.png",  # fallback for dark mode

    # Search models
    "search_model": ["accounts.CustomUser", "category.Category", "main.Product"],

    # Top menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "accounts"},
        {"app": "category"},
        {"app": "main"},
        {"name": "Website", "url": "https://mystore.com", "new_window": True},
    ],

    # Sidebar
    "show_sidebar": True,
    "navigation_expanded": True,

    # Hide clutter
    "hide_models": [
        "rest_framework_simplejwt.token_blacklist.BlacklistedToken",
        "rest_framework_simplejwt.token_blacklist.OutstandingToken",
        "auth.Group",
        "auth.Permission",
    ],

    # Custom icons
    "icons": {
        "accounts.CustomUser": "fas fa-user-circle",
        "accounts.EmailOTP": "fas fa-envelope",
        "category.Category": "fas fa-tags",
        "main.Product": "fas fa-box-open",
        "main.Order": "fas fa-shopping-cart",
    },

    # Ordering
    "order_with_respect_to": ["accounts", "category", "main"],

    # Custom assets
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_admin.js",
}

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
