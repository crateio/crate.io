from .base import *

from secret_settings import *
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
