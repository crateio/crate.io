import os

from .base import *

from local_settings import *  # Instance specific settings (in deploy.settings_[INSTANCE_NAME]))

# Fix Email Settings
SERVER_EMAIL = "server@crate.io"
DEFAULT_FROM_EMAIL = "support@crate.io"

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": ":".join([GONDOR_REDIS_HOST, str(GONDOR_REDIS_PORT)]),
        "KEY_PREFIX": "cache",
        "OPTIONS": {
            "DB": 0,
            "PASSWORD": GONDOR_REDIS_PASSWORD,
        }
    }
}

PYPI_DATASTORE_CONFIG = {
    "host": GONDOR_REDIS_HOST,
    "port": GONDOR_REDIS_PORT,
    "password": GONDOR_REDIS_PASSWORD,
}

LOCK_DATASTORE_CONFIG = PYPI_DATASTORE_CONFIG

# Configure Celery
BROKER_TRANSPORT = "redis"
BROKER_HOST = GONDOR_REDIS_HOST
BROKER_PORT = GONDOR_REDIS_PORT
BROKER_VHOST = "0"
BROKER_PASSWORD = GONDOR_REDIS_PASSWORD
BROKER_POOL_LIMIT = 10

CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = GONDOR_REDIS_HOST
CELERY_REDIS_PORT = GONDOR_REDIS_PORT
CELERY_REDIS_PASSWORD = GONDOR_REDIS_PASSWORD

SECRET_KEY = os.environ["SECRET_KEY"]

EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = int(os.environ["EMAIL_PORT"])
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": os.environ["HAYSTACK_DEFAULT_ENGINE"],
        "URL": os.environ["HAYSTACK_DEFAULT_URL"],
        "INDEX_NAME": os.environ["HAYSTACK_DEFAULT_INDEX_NAME"],
    },
}

INTERCOM_USER_HASH_KEY = os.environ["INTERCOM_USER_HASH_KEY"]
