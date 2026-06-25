"""
Base settings shared by all environments.
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# Read .env only when it actually exists (local dev).
# On production the shell environment already contains all variables.
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="change-me-in-env-at-least-32-chars!!")
DEBUG = env.bool("DEBUG", default=False)
TEST_MODE = env.bool("TEST_MODE", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

AUTH_USER_MODEL = "accounts.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "ninja",
    "corsheaders",
    "azbankgateways",
    # project apps
    "core",
    "sms",
    "notifications",
    "accounts",
    "store",
    "shipping",
    "payment",
    "blog",
    "admin_panel",
    "chatbot",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",        # ← اول
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database — dj-database-url / django-environ style
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# ---------------------------------------------------------------------------
# Auth validators
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# JWT (djangorestframework-simplejwt)
# ---------------------------------------------------------------------------
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------
# مدت اعتبار کد OTP بر حسب دقیقه (قابل override از env)
OTP_EXPIRY_MINUTES = env.int("OTP_EXPIRY_MINUTES", default=2)
# حداقل فاصله زمانی بین دو ارسال OTP بر حسب ثانیه
OTP_RATE_LIMIT_SECONDS = 60

# ---------------------------------------------------------------------------
# Pagination defaults
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ---------------------------------------------------------------------------
# SMS / Kavenegar
# ---------------------------------------------------------------------------
KAVENEGAR_API_KEY = env("KAVENEGAR_API_KEY", default="")
SMS_SENDER = env("SMS_SENDER", default="")

# ---------------------------------------------------------------------------
# Payment gateway
# ---------------------------------------------------------------------------
AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": env("ZARINPAL_MERCHANT_CODE", default="SANDBOX"),
            "SANDBOX": env.bool("PAYMENT_SANDBOX", default=True),
        },
    },
    "IS_SAMPLE_FORM_ENABLE": False,
    "DEFAULT": "ZARINPAL",
}
PAYMENT_CALLBACK_BASE_URL = env("PAYMENT_CALLBACK_BASE_URL", default="http://127.0.0.1:8000/api/payment/callback")
# آدرس فرانت‌اند — برای ریدایرکت بعد از callback پرداخت
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:3000")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True   # ← برای dev
CORS_ALLOW_CREDENTIALS = True
# ---------------------------------------------------------------------------
# Logging (base — console only; production overrides with file handlers)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
# Frontend revalidation webhook (PocketBase / React Query invalidation)
FRONTEND_REVALIDATE_URL    = env("FRONTEND_REVALIDATE_URL",    default="")
FRONTEND_REVALIDATE_SECRET = env("FRONTEND_REVALIDATE_SECRET", default="")
# ---------------------------------------------------------------------------
# PocketBase — sync محصولات
# ---------------------------------------------------------------------------
PB_URL            = env("PB_URL",            default="")
PB_ADMIN_EMAIL    = env("PB_ADMIN_EMAIL",    default="")
PB_ADMIN_PASSWORD = env("PB_ADMIN_PASSWORD", default="")
PB_FIND_ENDPOINT  = env("PB_FIND_ENDPOINT",  default="/api/collections/products_ui/records")
PB_SYNC_ENDPOINT  = env("PB_SYNC_ENDPOINT",  default="/api/collections/products_ui/records")
