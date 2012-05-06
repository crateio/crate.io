import os
import urlparse

from .base import *

if "GONDOR_DATABASE_URL" in os.environ:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["GONDOR_DATABASE_URL"])
    DATABASES = {
        "default": {
            "ENGINE": {
                "postgres": "django.db.backends.postgresql_psycopg2"
            }[url.scheme],
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port
        }
    }

if "GONDOR_REDIS_URL" in os.environ:
    urlparse.uses_netloc.append("redis")
    url = urlparse.urlparse(os.environ["GONDOR_REDIS_URL"])

    REDIS = {
        "default": {
            "HOST": url.hostname,
            "PORT": url.port,
            "PASSWORD": url.password,
        }
    }

    CACHES = {
       "default": {
            "BACKEND": "redis_cache.RedisCache",
            "LOCATION": "%(HOST)s:%(PORT)s" % REDIS["default"],
            "KEY_PREFIX": "cache",
            "OPTIONS": {
                "DB": 0,
                "PASSWORD": REDIS["default"]["PASSWORD"],
            }
        }
    }

    PYPI_DATASTORE = "default"

    LOCK_DATASTORE = "default"

    # Celery Broker
    BROKER_TRANSPORT = "redis"

    BROKER_HOST = REDIS["default"]["HOST"]
    BROKER_PORT = REDIS["default"]["PORT"]
    BROKER_PASSWORD = REDIS["default"]["PASSWORD"]
    BROKER_VHOST = "0"

    BROKER_POOL_LIMIT = 10

    # Celery Results
    CELERY_RESULT_BACKEND = "redis"

    CELERY_REDIS_HOST = REDIS["default"]["HOST"]
    CELERY_REDIS_PORT = REDIS["default"]["PORT"]
    CELERY_REDIS_PASSWORD = REDIS["default"]["PORT"]

MEDIA_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "media")
STATIC_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "static")

MEDIA_URL = "/site_media/media/"
STATIC_URL = "/site_media/static/"

FILE_UPLOAD_PERMISSIONS = 0640
