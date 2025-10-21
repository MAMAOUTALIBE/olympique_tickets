
from pathlib import Path
import os
import sys
from django.contrib.messages import constants as messages
import dj_database_url  # <-- assure-toi qu'il est dans requirements.txt
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # <- important: charge le .env local

# --------- Secrets & mode ---------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-unsafe")  # ⚠️ mettre une vraie clé en prod via config vars
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.herokuapp.com,https://localhost,https://127.0.0.1,http://localhost,http://127.0.0.1"
    ).split(",")
]

# --------- Apps / Middleware ---------
INSTALLED_APPS = [
    "sweetify",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tickets_bah",
    "appAdmin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Heroku static
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "olympique_tickets_bah.urls"
WSGI_APPLICATION = "olympique_tickets_bah.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# --------- Database (PostgreSQL / MariaDB) ---------
DB_ENGINE = os.getenv("DB_ENGINE", "postgresql").lower()

ENGINE_ALIASES = {
    "postgres": "django.db.backends.postgresql",
    "postgresql": "django.db.backends.postgresql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "mariadb": "django.db.backends.mysql",
    "mysql": "django.db.backends.mysql",
}

django_engine = ENGINE_ALIASES.get(DB_ENGINE, DB_ENGINE)

default_port = {
    "django.db.backends.postgresql": "5432",
    "django.contrib.gis.db.backends.postgis": "5432",
    "django.db.backends.mysql": "3306",
}.get(django_engine, "5432")

DATABASES = {
    "default": {
        "ENGINE": django_engine,
        "NAME": os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "postgres")),
        "USER": os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres")),
        "PASSWORD": os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
        "HOST": os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
        "PORT": os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", default_port)),
        "CONN_MAX_AGE": 600,
    }
}

if os.getenv("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=bool(os.getenv("DYNO")),
    )

TEST_RUNNER = "olympique_tickets_bah.test_runner.DefaultAppDiscoverRunner"

# --------- Static / Media ---------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------- Sécurité prod ---------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24  # ajuste si besoin
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# --------- Messages / Divers ---------
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "tickets_bah.Utilisateur"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------- E-mail (ne PAS hardcoder) ---------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend")
EMAIL_FILE_PATH = os.getenv("EMAIL_FILE_PATH", str(BASE_DIR / "sent_emails"))
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# --------- Stripe (via .env / config vars) ---------
# Accept both prod-style and *_TEST env vars so local .env.example works ootb
STRIPE_SECRET_KEY = (
    os.getenv("STRIPE_SECRET_KEY")
    or os.getenv("STRIPE_SECRET_KEY_TEST")
    or "secret"
)
STRIPE_PUBLIC_KEY = (
    os.getenv("STRIPE_PUBLIC_KEY")
    or os.getenv("STRIPE_PUBLIC_KEY_TEST")
    or "public"
)
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "secret")

# --------- Authentification email 2FA ---------
LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES = int(
    os.getenv("LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES", "10")
)
