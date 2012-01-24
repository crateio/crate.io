from ..base import *

SITE_ID = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SERVER_EMAIL = "server@crate.io"
DEFAULT_FROM_EMAIL = "support@crate.io"
CONTACT_EMAIL = "support@crate.io"

MIDDLEWARE_CLASSES += ["privatebeta.middleware.PrivateBetaMiddleware"]

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
# STATICFILES_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_STORAGE_BUCKET_NAME = "crate-production"

AWS_S3_CUSTOM_DOMAIN = "packages.crate.io"

PRIVATE_BETA_ALLOWED_URLS = [
    "/account/login/",
    "/account/signup/",
]
