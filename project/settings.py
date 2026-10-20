"""Environment based Django settings for local review and persistent hosting."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / os.getenv("MYBUD_ENV_FILE", ".env"))
IS_VERCEL = os.getenv("VERCEL") == "1"
DEBUG = os.getenv("DJANGO_DEBUG", "false" if IS_VERCEL else "true").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY when DJANGO_DEBUG=false.")
    secret_file = BASE_DIR / ".local-secret-key"
    try:
        with secret_file.open("x", encoding="utf-8") as handle:
            handle.write(get_random_secret_key())
    except FileExistsError:
        pass
    SECRET_KEY = secret_file.read_text(encoding="utf-8").strip()
    if len(SECRET_KEY) < 50:
        raise ImproperlyConfigured("Local secret file is invalid. Set DJANGO_SECRET_KEY.")
ALLOWED_HOSTS = [
    x.strip()
    for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if x.strip()
]
for host_variable in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    if IS_VERCEL and os.getenv(host_variable):
        ALLOWED_HOSTS.append(os.environ[host_variable])
MYBUD_MODE = os.getenv("MYBUD_MODE", "demo")
if MYBUD_MODE not in {"demo", "live"}:
    raise ImproperlyConfigured("MYBUD_MODE must be demo or live.")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
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
ROOT_URLCONF = "project.urls"
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
                "main.context_processors.identity",
            ]
        },
    }
]
WSGI_APPLICATION = "project.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3")),
        "OPTIONS": {"timeout": 20},
    }
}
if os.getenv("DATABASE_URL"):
    database = dj_database_url.parse(
        os.environ["DATABASE_URL"], conn_max_age=0, conn_health_checks=True, ssl_require=True
    )
    if database["ENGINE"] != "django.db.backends.postgresql":
        raise ImproperlyConfigured("DATABASE_URL must use PostgreSQL.")
    database["DISABLE_SERVER_SIDE_CURSORS"] = True
    database["OPTIONS"]["connect_timeout"] = 10
    DATABASES = {"default": database}
elif IS_VERCEL:
    raise ImproperlyConfigured("A persistent PostgreSQL DATABASE_URL is required on Vercel.")
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024
MYBUD_MAX_IMAGE_MB = int(os.getenv("MYBUD_MAX_IMAGE_MB", "3" if IS_VERCEL else "5"))
if not 1 <= MYBUD_MAX_IMAGE_MB <= 5:
    raise ImproperlyConfigured("MYBUD_MAX_IMAGE_MB must be between 1 and 5.")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = [
    x.strip() for x in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()
]
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
if os.getenv("DJANGO_TRUST_PROXY", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
