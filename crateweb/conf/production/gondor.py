import os

if "GONDOR_DATABASE_URL" in os.environ:
    os.environ.setdefault("DATABASE_URL", os.environ["GONDOR_DATABASE_URL"])

if "GONDOR_REDIS_URL" in os.environ:
    os.environ.setdefault("REDIS_URL", os.environ["GONDOR_REDIS_URL"])

from .base import *

MEDIA_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "media")
STATIC_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "static")

MEDIA_URL = "/site_media/media/"
STATIC_URL = "/site_media/static/"

FILE_UPLOAD_PERMISSIONS = 0640
