from ..base import *

DEBUG = True
TEMPLATE_DEBUG = True

SERVE_MEDIA = DEBUG

SITE_ID = 1

MIDDLEWARE_CLASSES += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += [
    "debug_toolbar",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

#CELERY_ALWAYS_EAGER = True  # When Testing Locally Use Eager
#CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Show Us Exceptions that Occur As Well

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
        "INDEX_NAME": "crate",
    },
}
