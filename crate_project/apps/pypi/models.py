from django.db import models

from model_utils import Choices
from model_utils.models import TimeStampedModel


class PyPIMirrorPage(models.Model):

    TYPES = Choices(
        ("simple", "Simple"),
        ("serversig", "Server Sig"),
    )

    package = models.ForeignKey("packages.Package")
    type = models.CharField(max_length=25, choices=TYPES)
    content = models.TextField()

    class Meta:
        unique_together = ("package", "type")

    def __unicode__(self):
        return "%(type)s: %(package)s" % {
            "type": self.get_type_display(),
            "package": self.package.name,
        }


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
