from ..base import *

DEBUG = True
TEMPLATE_DEBUG = True

SERVE_MEDIA = DEBUG
SERVE_LESS = DEBUG

SITE_ID = 1

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

MIDDLEWARE_CLASSES += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += [
    "debug_toolbar",
    "devserver",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEVSERVER_ARGS = [
    "--dozer",
]

DEVSERVER_IGNORED_PREFIXES = [
    "/site_media/",
]

DEVSERVER_MODULES = [
    # "devserver.modules.sql.SQLRealTimeModule",
    "devserver.modules.sql.SQLSummaryModule",
    "devserver.modules.profile.ProfileSummaryModule",

    # Modules not enabled by default
    "devserver.modules.ajax.AjaxDumpModule",
    "devserver.modules.cache.CacheSummaryModule",
    "devserver.modules.profile.LineProfilerModule",
]

# Configure Celery
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"
BROKER_PASSWORD = None
BROKER_POOL_LIMIT = 10

CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_PASSWORD = None

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "crate-dev",
    },
}

# Storage for Packages
PACKAGE_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
PACKAGE_FILE_STORAGE_OPTIONS = {
    "bucket": "crate-dev",
}
PACKAGE_DELETE_REQUIRED = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_STORAGE_BUCKET_NAME = "crate-media-dev"

SIMPLE_API_URL = "http://simple.crate.io/"
