from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from model_utils import Choices
from model_utils.models import TimeStampedModel


class PyPIMirrorPage(TimeStampedModel):

    package = models.ForeignKey("packages.Package", unique=True)
    content = models.TextField()

    def __unicode__(self):
        return self.package.name

    def get_relative_url(self, current_url):
        absolute_url_split = reverse("pypi_package_detail", kwargs={"slug": self.package.name}).split("/")
        current_url_split = current_url.split("/")

        relative_url_split = absolute_url_split[:]
        for i, part in enumerate(absolute_url_split):
            if len(current_url_split) > i and part == current_url_split[i]:
                relative_url_split = relative_url_split[1:]

        return "/".join(relative_url_split)


class PyPIServerSigPage(TimeStampedModel):

    package = models.ForeignKey("packages.Package")
    content = models.TextField()

    def __unicode__(self):
        return self.package.name


class PyPIIndexPage(TimeStampedModel):

    content = models.TextField()

    def __unicode__(self):
        return "PyPI Index Page: %s" % self.created.isoformat()


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


# @receiver(post_save, sender=PyPIMirrorPage)
# @receiver(post_delete, sender=PyPIMirrorPage)
def regenerate_simple_index(sender, **kwargs):
    from pypi.tasks import refresh_pypi_package_index_cache
    refresh_pypi_package_index_cache.delay()
