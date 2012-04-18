from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from model_utils.fields import AutoCreatedField, AutoLastModifiedField
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


class PyPIIndexPage(models.Model):

    created = AutoCreatedField("created", db_index=True)
    modified = AutoLastModifiedField("modified")

    content = models.TextField()

    def __unicode__(self):
        return "PyPI Index Page: %s" % self.created.isoformat()


class PyPIDownloadChange(TimeStampedModel):

    file = models.ForeignKey("packages.ReleaseFile")
    change = models.IntegerField(default=0)
    integrated = models.BooleanField(default=False)


@receiver(post_save, sender=PyPIMirrorPage)
@receiver(post_delete, sender=PyPIMirrorPage)
def regenerate_simple_index(sender, **kwargs):
    from pypi.tasks import refresh_pypi_package_index_cache
    refresh_pypi_package_index_cache.delay()
