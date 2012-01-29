from django.db import models

from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel

from uuidfield import UUIDField

from packages.models import ReleaseFile


class Log(TimeStampedModel):
    TYPES = Choices(
        ("sync", "Synchronize Mirror"),
        ("package", "Synchronize Package"),
        ("version", "Synchronize Package Version"),
    )

    type = models.CharField(max_length=50, choices=TYPES)
    index = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        return self.message


class ChangeLog(TimeStampedModel):
    package = models.CharField(max_length=150)
    version = models.CharField(max_length=150, null=True, blank=True)
    timestamp = models.DateTimeField()
    action = models.TextField(blank=True, null=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __unicode__(self):
        return u"%(package)s %(version)s %(timestamp)s %(action)s" % {
            "package": self.package,
            "version": self.version,
            "timestamp": self.timestamp,
            "action": self.action,
        }


class PackageModified(TimeStampedModel):
    release_file = models.ForeignKey(ReleaseFile, related_name="+")

    url = models.TextField(unique=True)
    last_modified = models.CharField(max_length=150)
    md5 = models.CharField(max_length=32)

    def __unicode__(self):
        return u"%(url)s - %(modified)s - %(hash)s" % {
            "url": self.url,
            "modified": self.last_modified,
            "hash": self.md5,
        }


class TaskLog(TimeStampedModel):
    STATUS = Choices(
        ("success", "Success"),
        ("failed", "Failed"),
        ("retry", "Retry"),
    )

    task_id = UUIDField(auto=False, editable=True, unique=True)
    status = StatusField()
    name = models.CharField(max_length=300)
    args = models.TextField()
    kwargs = models.TextField()
    exception = models.TextField(blank=True)


class DownloadChange(TimeStampedModel):
    release = models.ForeignKey("packages.Release")
    change = models.IntegerField(default=0)
