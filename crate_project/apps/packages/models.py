import os

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum

from django_hstore import hstore
from model_utils import Choices
from model_utils.models import TimeStampedModel

from crate.fields import JSONField


# @@@ These are by Nature Hierarchical. Would we benefit from a tree structure?
class TroveClassifier(models.Model):
    trove = models.CharField(max_length=350, unique=True)

    def __unicode__(self):
        return self.trove


class Package(TimeStampedModel):
    name = models.SlugField(max_length=150, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"name": self.name})

    @property
    def summary(self):
        if not hasattr(self, "_latest_release"):
            try:
                self._latest_release = self.releases.latest()
            except Release.DoesNotExist:
                self._latest_release = None

        if self._latest_release is not None:
            return self._latest_release.summary

    @property
    def description(self):
        if not hasattr(self, "_latest_release"):
            try:
                self._latest_release = self.releases.latest()
            except Release.DoesNotExist:
                self._latest_release = None

        if self._latest_release is not None:
            return self._latest_release.description

    @property
    def version(self):
        try:
            latest_release = self.releases.latest()
        except Release.DoesNotExist:
            return
        return latest_release.version

    @property
    def downloads(self):
        total_downloads = ReleaseFile.objects.filter(release__package__pk=self.pk).aggregate(total_downloads=Sum("downloads"))["total_downloads"]
        if total_downloads is None:
            return 0
        return total_downloads


class Release(TimeStampedModel):
    package = models.ForeignKey(Package, related_name="releases")
    version = models.CharField(max_length=512)

    hidden = models.BooleanField(default=False)

    platform = models.TextField(blank=True)

    summary = models.TextField()
    description = models.TextField(blank=True)

    keywords = models.TextField(blank=True)

    license = models.TextField(blank=True)

    author = models.TextField(blank=True)
    author_email = models.TextField(blank=True)

    maintainer = models.TextField(blank=True)
    maintainer_email = models.TextField(blank=True)

    requires_python = models.CharField(max_length=25, blank=True)

    download_uri = models.URLField(max_length=1024, blank=True)
    uris = hstore.DictionaryField()

    classifiers = models.ManyToManyField(TroveClassifier, related_name="releases", blank=True)

    raw_data = JSONField(null=True)

    objects = hstore.Manager()

    class Meta:
        unique_together = ("package", "version")
        get_latest_by = "created"  # @@@ Change this to use ordering

    def __unicode__(self):
        return u"%(package)s %(version)s" % {"package": self.package.name, "version": self.version}


class ReleaseFile(TimeStampedModel):
    release = models.ForeignKey(Release, related_name="files")

    type = models.CharField(max_length=25)
    file = models.FileField(upload_to="packages", max_length=512)
    filename = models.CharField(max_length=200, help_text="This is the file name given to us by PyPI", blank=True, null=True, default=None)
    digest = models.CharField(max_length=512)

    python_version = models.CharField(max_length=25)

    downloads = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("release", "type", "python_version", "filename")

    def __unicode__(self):
        return os.path.basename(self.file.name)


class ReleaseRequire(models.Model):

    KIND = Choices(
        ("requires", "Requirement"),
        ("requires_dist", "Dist Requirement"),
        ("external", "External Requirement"),
    )

    release = models.ForeignKey(Release, related_name="requires")

    kind = models.CharField(max_length=50, choices=KIND)
    name = models.CharField(max_length=150)
    version = models.CharField(max_length=50)

    environment = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class ReleaseProvide(models.Model):

    KIND = Choices(
        ("provides", "Provides"),
        ("provides_dist", "Dist Provides"),
    )

    release = models.ForeignKey(Release, related_name="provides")

    kind = models.CharField(max_length=50, choices=KIND)
    name = models.CharField(max_length=150)
    version = models.CharField(max_length=50)

    environment = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class ReleaseObsolete(models.Model):

    KIND = Choices(
        ("obsoletes", "Obsoletes"),
        ("obsoletes_dist", "Dist Obsoletes"),
    )

    release = models.ForeignKey(Release, related_name="obsoletes")

    kind = models.CharField(max_length=50, choices=KIND)
    name = models.CharField(max_length=150)
    version = models.CharField(max_length=50)

    environment = models.TextField(blank=True)

    def __unicode__(self):
        return self.name
