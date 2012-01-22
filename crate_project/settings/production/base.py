from ..base import *

SITE_ID = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEFAULT_FROM_EMAIL = "support@crate.io"

MIDDLEWARE_CLASSES += ["privatebeta.middleware.PrivateBetaMiddleware"]

PRIVATE_BETA_ALLOWED_URLS = [
    "/account/login/",
    "/account/signup/",
]
