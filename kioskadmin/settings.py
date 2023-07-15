"""
Django settings for kioskadmin project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import requests

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "mozilla_django_oidc",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "kiosksvc"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend',
    # 'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    "kioskadmin.oidc_auth.MyOIDCAuthBackend",
]

ROOT_URLCONF = "kioskadmin.urls"

SRC_DIR = Path(__file__).resolve().parent


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR.joinpath("templates")],
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

WSGI_APPLICATION = "kioskadmin.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email Config
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_SENDER_NAME = os.environ["EMAIL_SENDER_NAME"]
EMAIL_EVENT_NAME = os.environ["EMAIL_EVENT_NAME"]

# OIDC Config
OIDC_CONFIG_BASEURL = os.environ["OIDC_CONFIG_BASEURL"]
try:
    oidc_document = requests.get(
        f"{OIDC_CONFIG_BASEURL}/.well-known/openid-configuration"
    ).json()
    OIDC_OP_AUTHORIZATION_ENDPOINT = oidc_document["authorization_endpoint"]
    OIDC_OP_TOKEN_ENDPOINT = oidc_document["token_endpoint"]
    OIDC_OP_USER_ENDPOINT = oidc_document["userinfo_endpoint"]
    OIDC_OP_JWKS_ENDPOINT = oidc_document["jwks_uri"]
except requests.exceptions.ConnectionError:
    print("Skipping configuration for OIDC! It won't work correctly")
    OIDC_OP_AUTHORIZATION_ENDPOINT = None
    OIDC_OP_TOKEN_ENDPOINT = None
    OIDC_OP_USER_ENDPOINT = None
    OIDC_OP_JWKS_ENDPOINT = None

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_CLIENT_ID = os.environ["OIDC_RP_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["OIDC_RP_CLIENT_SECRET"]
LOGIN_REDIRECT_URL = "/admin"
LOGOUT_REDIRECT_URL = "/admin/logout"
OIDC_CREATE_USER = True  # Disable Django User Automatic Creation from OIDC
OIDC_USERNAME_ALGO = "kioskadmin.oidc_auth.generate_username"

# Key pair for Check-IN QR JWT
CHECKIN_QR_CONFIG = {
    "private_key_path": os.environ["CHECKIN_QR_JWT_PRIVATE_KEY_PATH"],
    "public_key_path": os.environ["CHECKIN_QR_JWT_PUBLIC_KEY_PATH"],
}
