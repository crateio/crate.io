from ..base import *

SITE_ID = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEFAULT_FROM_EMAIL = "donald@crate.io"
CONTACT_EMAIL = "donald@crate.io"

MIDDLEWARE_CLASSES += ["privatebeta.middleware.PrivateBetaMiddleware"]

DEFAULT_FILE_STORAGE = "cumulus.storage.CloudFilesStorage"

CUMULUS_CONTAINER = "crate-production"

PRIVATE_BETA_ALLOWED_URLS = [
    "/account/login/",
    "/account/signup/",
]
