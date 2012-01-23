from ..base import *

SITE_ID = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SERVER_EMAIL = "server@crate.io"
DEFAULT_FROM_EMAIL = "donald@crate.io"
CONTACT_EMAIL = "donald@crate.io"

MIDDLEWARE_CLASSES += ["privatebeta.middleware.PrivateBetaMiddleware"]

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
STATICFILES_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_STORAGE_BUCKET_NAME = "crate-production"

PRIVATE_BETA_ALLOWED_URLS = [
    "/account/login/",
    "/account/signup/",
]
