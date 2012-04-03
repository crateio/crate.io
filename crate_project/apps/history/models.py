from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from jsonfield import JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel

from packages.models import Package, Release, ReleaseFile


class Event(TimeStampedModel):

    ACTIONS = Choices(
            ("package_create", "Package Created"),
            ("package_delete", "Package Deleted"),
            ("release_create", "Release Created"),
            ("release_delete", "Release Deleted"),
            ("file_add", "File Added"),
            ("file_remove", "File Removed"),
        )

    package = models.SlugField(max_length=150)
    version = models.CharField(max_length=512, blank=True)

    action = models.CharField(max_length=25, choices=ACTIONS)

    data = JSONField(null=True, blank=True)


@receiver(post_save, sender=Package)
def history_package_create(instance, created, **kwargs):
    if created:
        Event.objects.create(
            package=instance.name,
            action=Event.ACTIONS.package_create
        )


@receiver(post_delete, sender=Package)
def history_package_delete(instance, **kwargs):
    Event.objects.create(
        package=instance.name,
        action=Event.ACTIONS.package_delete
    )


@receiver(post_save, sender=Release)
def history_release_update(instance, created, **kwargs):
    if created:
        Event.objects.create(
            package=instance.package.name,
            version=instance.version,
            action=Event.ACTIONS.release_create
        )

    if instance.has_changed("hidden"):
        if instance.hidden:
            Event.objects.create(
                package=instance.package.name,
                version=instance.version,
                action=Event.ACTIONS.release_delete
            )
        else:
            Event.objects.create(
                package=instance.package.name,
                version=instance.version,
                action=Event.ACTIONS.release_create
            )


@receiver(post_save, sender=ReleaseFile)
def history_releasefile_update(instance, created, **kwargs):
    e = None

    if instance.has_changed("file"):
        e = Event.objects.create(
            package=instance.release.package.name,
            version=instance.release.version,
            action=Event.ACTIONS.file_add
        )
    else:
        if instance.has_changed("hidden"):
            if instance.hidden:
                e = Event.objects.create(
                    package=instance.release.package.name,
                    version=instance.release.version,
                    action=Event.ACTIONS.file_remove
                )
            else:
                e = Event.objects.create(
                    package=instance.release.package.name,
                    version=instance.release.version,
                    action=Event.ACTIONS.file_add
                )
    if e is not None:
        e.data = {
            "filename": instance.filename,
            "digest": instance.digest,
            "uri": instance.get_absolute_url(),
        }
        e.save()
