
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

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.herokuapp.com,https://localhost,https://127.0.0.1"
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

# --------- Database (Heroku + fallback local) ---------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "postgres://olympique_user:MotDePasse_App14!@127.0.0.1:5432/tickets_olympique_bah"  # fallback dev local
        ),
        conn_max_age=600,
        ssl_require=bool(os.getenv("DYNO")),  # True sur Heroku
    )
}

USE_SQLITE_FOR_TESTS = os.getenv("USE_SQLITE_FOR_TESTS", "").lower() in {"1", "true", "yes"} or "test" in sys.argv

if USE_SQLITE_FOR_TESTS:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }

TEST_RUNNER = "olympique_tickets_bah.test_runner.DefaultAppDiscoverRunner"

# --------- Static / Media ---------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
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
