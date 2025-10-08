from pathlib import Path
import os
from django.contrib.messages import constants as messages


MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY_TEST', "secret")
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY_TEST', "public")


#from tickets_bah import static

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-4&x#ke^@-8d1-25(ztbg4h56f6x#0y-mqr=ll3+-v=zyefnk%z"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.ngrok-free.app', 'localhost', '127.0.0.1']


# Application definition

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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "olympique_tickets_bah.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "olympique_tickets_bah.wsgi.application"

# Paramètres pour l'envoi d'e-mails
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'  # Serveur SMTP
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = 'bahm2062@gmail.com'  # Remplacez par votre email
#EMAIL_HOST_PASSWORD = 'BAHmamadou2008@'  # Remplacez par votre mot de passe ou App Password
#DEFAULT_FROM_EMAIL = 'noreply@gmail.com'


# Paramètres pour l'envoi d'e-mails
## settings.py (dev)
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'bahm2062@gmail.com'  # Remplacez par votre email
EMAIL_HOST_PASSWORD = 'eypxafftszttbngv'  # Remplacez par votre mot de passe ou App Password
DEFAULT_FROM_EMAIL = 'noreply@gmail.com'



# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

ALLOWED_HOSTS = ["olympique-tickets-bah.herokuapp.com", "localhost", "127.0.0.1"]
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DB_NAME"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST", "127.0.0.1"),
    "PORT": os.getenv("DB_PORT", "5432"),
  }
}

    #"default": {
        #"ENGINE": "django.db.backends.sqlite3",
        #"NAME": BASE_DIR / "db.sqlite3",
        #"USER": "username", #postgres
        #"PASSWORD": "password",
        #"HOST": "localhost",  # ou l'IP du serveur PostgreSQL
        #"PORT": "5432",       # port par défaut de PostgreSQL
    #}
#}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = 'tickets_bah.Utilisateur'


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = '/'  # Par exemple, la page d'accueil

# Configuration de Sweetify
SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'


STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY_TEST', "secret")

STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', "secret")