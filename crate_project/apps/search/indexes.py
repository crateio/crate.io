from django.db.models import signals

from celery_haystack.indexes import CelerySearchIndex as BaseCelerySearchIndex

from packages.models import Package, Release, ReleaseFile


class PackageCelerySearchIndex(BaseCelerySearchIndex):

    # We override the built-in _setup_* methods to connect the enqueuing
    # operation.
    def _setup_save(self, model=None):
        model = self.handle_model(model)
        signals.post_save.connect(self.enqueue_save, sender=model)
        signals.post_save.connect(self.enqueue_save_from_release, sender=Release)
        signals.post_save.connect(self.enqueue_save_from_releasefile, sender=ReleaseFile)

    def _setup_delete(self, model=None):
        model = self.handle_model(model)
        signals.post_delete.connect(self.enqueue_delete, sender=model)
        signals.post_delete.connect(self.enqueue_delete_from_release, sender=Release)
        signals.post_delete.connect(self.enqueue_delete_from_releasefile, sender=ReleaseFile)

    def _teardown_save(self, model=None):
        model = self.handle_model(model)
        signals.post_save.disconnect(self.enqueue_save, sender=model)
        signals.post_save.disconnect(self.enqueue_save_from_release, sender=Release)
        signals.post_save.disconnect(self.enqueue_save_from_releasefile, sender=ReleaseFile)

    def _teardown_delete(self, model=None):
        model = self.handle_model(model)
        signals.post_delete.disconnect(self.enqueue_delete, sender=model)
        signals.post_delete.disconnect(self.enqueue_delete_from_release, sender=Release)
        signals.post_delete.disconnect(self.enqueue_delete_from_releasefile, sender=ReleaseFile)

    def enqueue_save_from_release(self, instance, **kwargs):
        return self.enqueue('update', instance.package)

    def enqueue_delete_from_release(self, instance, **kwargs):
        try:
            return self.enqueue('update', instance.package)
        except Package.DoesNotExist:
            pass

    def enqueue_save_from_releasefile(self, instance, **kwargs):
        return self.enqueue('update', instance.release.package)

    def enqueue_delete_from_releasefile(self, instance, **kwargs):
        try:
            return self.enqueue('update', instance.release.package)
        except Release.DoesNotExist:
            pass
