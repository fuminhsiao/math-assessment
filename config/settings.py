from pathlib import Path
import os

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Local development falls back to a demo key. On Render, set DJANGO_SECRET_KEY
# (or SECRET_KEY) as an environment variable.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    os.getenv("SECRET_KEY", "django-insecure-demo-only-change-me"),
)

# Keep DEBUG on locally, but turn it off automatically on Render.
DEBUG = os.getenv("DJANGO_DEBUG", "False" if os.getenv("RENDER") else "True").lower() == "true"

# Local + ngrok + Render hosts.
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".ngrok-free.dev",
    ".ngrok-free.app",
    ".onrender.com",
]

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://*.ngrok-free.app",
    "https://*.onrender.com",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "assessments",
]

MIDDLEWARE = [
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Locally this uses db.sqlite3. On Render, set DATABASE_URL to the Internal
# Database URL from your Render Postgres instance.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Boise"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
