# -*- coding: utf-8 -*-

import os.path
import datetime
import posixpath
import time

from django.utils.http import http_date

import djcelery

djcelery.setup_loader()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

DEBUG = False
TEMPLATE_DEBUG = True

SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "crate",
    }
}

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

USE_I18N = False
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
MEDIA_URL = "/site_media/media/"


STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")
STATIC_URL = "/site_media/static/"

ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

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

TEMPLATE_LOADERS = [
    ("django.template.loaders.cached.Loader", [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]),
]

MIDDLEWARE_CLASSES = [
    "django_hosts.middleware.HostsMiddleware",
    "djangosecure.middleware.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "pagination.middleware.PaginationMiddleware",

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

JINJA_TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates", "_jinja2"),
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
    # Admin Dashboard
    "admin_tools",
    "admin_tools.theming",
    "admin_tools.menu",
    "admin_tools.dashboard",

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
    "pagination",
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
    "storages",
    "intercom",
    "celery_haystack",
    "tastypie",
    "djangosecure",

    # project
    "about",
    "aws_stats",
    "profiles",
    "packages",
    "pypi",
    "search",
    "crate",
    "evaluator",
    "favorites",
    "history",
    "helpdocs",
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

CONTACT_EMAIL = "support@crate.io"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = True

AUTHENTICATION_BACKENDS = [
    "pinax.apps.account.auth_backends.AuthenticationBackend",
]

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.SHA1PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.CryptPasswordHasher",
)

LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "what_next"
LOGOUT_REDIRECT_URLNAME = "search"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TASK_PUBLISH_RETRY = True

CELERYD_MAX_TASKS_PER_CHILD = 10000

CELERY_IGNORE_RESULT = True

CELERY_TASK_RESULT_EXPIRES = 7 * 24 * 60 * 60  # 7 Days

CELERYD_HIJACK_ROOT_LOGGER = False

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15

AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False

AWS_HEADERS = {
    "Expires": lambda: http_date(time.mktime((datetime.datetime.now() + datetime.timedelta(days=365)).timetuple())),
    "Cache-Control": "max-age=31556926",
}


METRON_SETTINGS = {
    "google": {3: "UA-28759418-1"},
    "gauges": {3: "4f1e4cd0613f5d7003000002"}
}

ADMIN_TOOLS_INDEX_DASHBOARD = "crate.dashboard.CrateIndexDashboard"
