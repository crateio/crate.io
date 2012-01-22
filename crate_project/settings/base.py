# -*- coding: utf-8 -*-
# Django settings for basic pinax project.

import os.path
import posixpath

import djcelery

djcelery.setup_loader()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

DEBUG = False
TEMPLATE_DEBUG = True

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django_hstore.postgresql_psycopg2",
        "NAME": "crate",
    }
}

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
MEDIA_URL = "/site_media/media/"


STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")
STATIC_URL = "/site_media/static/"

STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_OUTPUT_DIR = "cache"

SECRET_KEY = ")ys)^6l18seiq)veen^41ox%l@6#o-2t*9-8n5$7$f+qi*x03$"

TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django_hosts.middleware.HostsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "pinax.apps.account.middleware.LocaleMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
]

ROOT_URLCONF = "crate_project.urls"
ROOT_HOSTCONF = "crate_project.hosts"

DEFAULT_HOST = "default"

WSGI_APPLICATION = "crate_project.wsgi.application"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",

    "staticfiles.context_processors.static",

    "pinax.core.context_processors.pinax_settings",

    "pinax.apps.account.context_processors.account",

    # "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.markup",

    "pinax.templatetags",

    # theme
    "pinax_theme_bootstrap",

    # external (Pinax)
    # "notification",  # must be first
    "staticfiles",
    "compressor",
    "django_openid",
    "timezones",
    "emailconfirmation",
    "announcements",
    "idios",
    "metron",

    # Pinax
    "pinax.apps.account",
    "pinax.apps.signup_codes",

    # external (Project)
    "south",
    "djcelery",
    "django_hosts",
    "haystack",
    "cumulus",

    # project
    "about",
    "profiles",
    "packages",
    "pypi",
    "search",
    "crate",
    "privatebeta",
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = False
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = True

AUTHENTICATION_BACKENDS = [
    "pinax.apps.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "what_next"
LOGOUT_REDIRECT_URLNAME = "search"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

SOUTH_DATABASE_ADAPTERS = {
    "default": "south.db.postgresql_psycopg2",
}

CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TASK_PUBLISH_RETRY = True

CELERY_TASK_RESULT_EXPIRES = 7 * 24 * 60 * 60  # 7 Days
CELERYD_TASK_TIME_LIMIT = 120
CELERYD_TASK_SOFT_TIME_LIMIT = 30

CELERYD_HIJACK_ROOT_LOGGER = False

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15
