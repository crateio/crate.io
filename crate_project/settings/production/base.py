import datetime

from ..base import *

SITE_ID = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SERVER_EMAIL = "server@crate.io"
DEFAULT_FROM_EMAIL = "donald@crate.io"
CONTACT_EMAIL = "donald@crate.io"

MIDDLEWARE_CLASSES += ["privatebeta.middleware.PrivateBetaMiddleware"]

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
STATICFILES_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_STORAGE_BUCKET_NAME = ""

AWS_HEADERS = {
    "Expires": lambda x: (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    "Cache-Control": "max-age=31556926",
}


PRIVATE_BETA_ALLOWED_URLS = [
    "/account/login/",
    "/account/signup/",
]
