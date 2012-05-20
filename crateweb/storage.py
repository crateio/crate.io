from django.conf import settings
from staticfiles.storage import CachedFilesMixin
from storages.backends.s3boto import S3BotoStorage


class CachedStaticS3BotoStorage(CachedFilesMixin, S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs.update(getattr(settings, "STATICFILES_S3_OPTIONS", {}))
        super(CachedStaticS3BotoStorage, self).__init__(*args, **kwargs)
