"""
Production settings.

Set DJANGO_SETTINGS_MODULE=config.settings.production on the server.
All secrets MUST be present in the environment — never hard-coded here.

Local "check" usage (Windows dev):
    python manage.py check --settings=config.settings.production
    → Works as long as .env contains at least placeholder values for
      SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS.
"""
import os
import logging.handlers  # noqa: F401 — imported early so handlers dict is valid

import environ

from .base import (  # explicit imports — no star import — avoids mutation issues
    BASE_DIR,
    INSTALLED_APPS,
    MIDDLEWARE,
    ROOT_URLCONF,
    TEMPLATES,
    WSGI_APPLICATION,
    AUTH_USER_MODEL,
    AUTH_PASSWORD_VALIDATORS,
    LANGUAGE_CODE,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    STATIC_URL,
    STATIC_ROOT,
    MEDIA_URL,
    MEDIA_ROOT,
    SIMPLE_JWT,
    OTP_EXPIRY_MINUTES,
    OTP_RATE_LIMIT_SECONDS,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    KAVENEGAR_API_KEY,
    SMS_SENDER,
    PAYMENT_CALLBACK_BASE_URL,
    FRONTEND_BASE_URL,
    CORS_ALLOW_CREDENTIALS,
    DEFAULT_AUTO_FIELD,
    STATICFILES_STORAGE,
)

env = environ.Env()

_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# ---------------------------------------------------------------------------
# Media — persistent disk (Runflare mounts /app/media)
# ---------------------------------------------------------------------------
MEDIA_ROOT = "/app/media"
MEDIA_URL = "/media/"
STATIC_ROOT = "/app/staticfiles"

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")  # raises ImproperlyConfigured if missing — intentional
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["farzam.runflare.run", "localhost", "127.0.0.1"])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)

USE_SSL = env.bool("USE_SSL", default=False)

SESSION_COOKIE_SECURE = USE_SSL
CSRF_COOKIE_SECURE = USE_SSL
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000 if USE_SSL else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_SSL
SECURE_HSTS_PRELOAD = USE_SSL

# ---------------------------------------------------------------------------
# Database (PostgreSQL required in production)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL"),  # raises ImproperlyConfigured if missing — intentional
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"].setdefault("OPTIONS", {})
DATABASES["default"]["OPTIONS"]["connect_timeout"] = 10

# ---------------------------------------------------------------------------
# Static files — WhiteNoise
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")

# ---------------------------------------------------------------------------
# Payment gateway — redefine in full (do NOT mutate the base dict)
# ---------------------------------------------------------------------------
AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": env("ZARINPAL_MERCHANT_CODE", default="sandbox"),
            "SANDBOX": env.bool("PAYMENT_SANDBOX", default=False),
        },
    },
    "IS_SAMPLE_FORM_ENABLE": False,
    "DEFAULT": "ZARINPAL",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "https://front-farzam.runflare.run",
])

# ---------------------------------------------------------------------------
# CSRF Trusted Origins
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[
    "https://farzam.runflare.run",
    "https://front-farzam.runflare.run",
])

# ---------------------------------------------------------------------------
# Logging — rotating files + console
# ---------------------------------------------------------------------------
LOG_DIR = env("LOG_DIR", default="/app/logs")
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    _log_writable = os.access(LOG_DIR, os.W_OK)
except OSError:
    _log_writable = False

_file_handlers = ["file", "error_file"] if _log_writable else []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} pid={process:d} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django_errors.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "level": "ERROR",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console"] + (["file"] if _log_writable else []),
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"] + _file_handlers,
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}