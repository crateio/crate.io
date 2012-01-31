import os
import posixpath
import urlparse
import uuid

import lxml.html

from docutils.core import publish_string

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from model_utils.models import TimeStampedModel

from crate.fields import JSONField
from packages.utils import verlib

# Get the Storage Engine for Packages
if getattr(settings, "PACKAGE_FILE_STORAGE", None):
    mod_name, engine_name = settings.PACKAGE_FILE_STORAGE.rsplit(".", 1)
    mod = import_module(mod_name)
    package_storage = getattr(mod, engine_name)(**getattr(settings, "PACKAGE_FILE_STORAGE_OPTIONS", {}))
else:
    package_storage = None


def release_file_upload_to(instance, filename):
    dsplit = instance.digest.split("$")
    if len(dsplit) == 2:
        directory = dsplit[1]
    else:
        directory = str(uuid.uuid4()).replace("-", "")

    if getattr(settings, "PACKAGE_FILE_STORAGE_BASE_DIR", None):
        path_items = [settings.PACKAGE_FILE_STORAGE_BASE_DIR]
    else:
        path_items = []

    for char in directory[:4]:
        path_items.append(char)

    path_items += [directory, filename]

    return posixpath.join(*path_items)


# @@@ These are by Nature Hierarchical. Would we benefit from a tree structure?
class TroveClassifier(models.Model):
    trove = models.CharField(max_length=350, unique=True)

    def __unicode__(self):
        return self.trove


class Package(TimeStampedModel):
    name = models.SlugField(max_length=150, unique=True)
    downloads_synced_on = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"package": self.name})

    @property
    def downloads(self):
        total_downloads = ReleaseFile.objects.filter(release__package__pk=self.pk).aggregate(total_downloads=Sum("downloads"))["total_downloads"]
        if total_downloads is None:
            return 0
        return total_downloads

    @property
    def latest(self):
        if not hasattr(self, "_latest_release"):
            releases = self.releases.order_by("-order")[:1]
            if releases:
                self._latest_release = releases[0]
            else:
                self._latest_release = None
        return self._latest_release

    @property
    def install_command(self):
        return "pip install %(package)s" % {"package": self.name}

    @property
    def requirement_line(self):
        if self.latest is not None:
            return "%(package)s==%(version)s" % {"package": self.name, "version": self.latest.version}


class PackageURI(models.Model):
    package = models.ForeignKey(Package, related_name="package_links")
    uri = models.URLField(max_length=400)

    class Meta:
        unique_together = ["package", "uri"]

    def __unicode__(self):
        return self.uri


class Release(models.Model):

    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"))

    package = models.ForeignKey(Package, related_name="releases")
    version = models.CharField(max_length=512)

    hidden = models.BooleanField(default=False)

    order = models.IntegerField(default=0)

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

    classifiers = models.ManyToManyField(TroveClassifier, related_name="releases", blank=True)

    raw_data = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ("package", "version")

    def __unicode__(self):
        return u"%(package)s %(version)s" % {"package": self.package.name, "version": self.version}

    def save(self, *args, **kwargs):
        # Update the Project's URIs
        docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})

        docutils_settings.update({"warning_stream": os.devnull})

        try:
            html_string = publish_string(source=smart_str(self.description), writer_name="html4css1", settings_overrides=docutils_settings)
            if html_string.strip():
                html = lxml.html.fromstring(html_string)

                for link in html.xpath("//a/@href"):
                    try:
                        if any(urlparse.urlparse(link)[:5]):
                            PackageURI.objects.get_or_create(package=self.package, uri=link)
                    except ValueError:
                        pass
        except Exception:
            # @@@ We Swallow Exceptions here, but it's the best way that I can think of atm.
            pass

        return super(Release, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"package": self.package.name, "version": self.version})

    @property
    def downloads(self):
        total_downloads = ReleaseFile.objects.filter(release__pk=self.pk).aggregate(total_downloads=Sum("downloads"))["total_downloads"]
        if total_downloads is None:
            return 0
        return total_downloads

    @property
    def install_command(self):
        return "pip install %(package)s==%(version)s" % {"package": self.package.name, "version": self.version}

    @property
    def requirement_line(self):
        return "%(package)s==%(version)s" % {"package": self.package.name, "version": self.version}


class ReleaseFile(models.Model):

    TYPES = Choices(
        ("sdist", "Source"),
        ("bdist_egg", "Egg"),
        ("bdist_msi", "MSI"),
        ("bdist_dmg", "DMG"),
        ("bdist_rpm", "RPM"),
        ("bdist_dumb", "bdist_dumb"),
        ("bdist_wininst", "bdist_wininst"),
    )

    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"))

    release = models.ForeignKey(Release, related_name="files")

    type = models.CharField(max_length=25, choices=TYPES)
    file = models.FileField(upload_to=release_file_upload_to, storage=package_storage, max_length=512)
    filename = models.CharField(max_length=200, help_text="This is the file name given to us by PyPI", blank=True, null=True, default=None)
    digest = models.CharField(max_length=512)

    python_version = models.CharField(max_length=25)

    downloads = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("release", "type", "python_version", "filename")

    def __unicode__(self):
        return os.path.basename(self.file.name)

    def get_absolute_url(self):
        return self.file.url

    def get_python_version_display(self):
        if self.python_version.lower() == "source":
            return ""
        return self.python_version


class ReleaseURI(models.Model):
    release = models.ForeignKey(Release, related_name="uris")
    label = models.CharField(max_length=64)
    uri = models.URLField(max_length=500)


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


class ChangeLog(TimeStampedModel):

    TYPES = Choices(
        ("new", "New"),
        ("updated", "Updated"),
    )

    type = models.CharField(max_length=25, choices=TYPES)
    package = models.ForeignKey(Package)
    release = models.ForeignKey(Release, blank=True, null=True)


@receiver(post_save, sender=Release)
def version_ordering(sender, **kwargs):
    instance = kwargs.get("instance")
    if instance is not None:
        releases = Release.objects.filter(package__pk=instance.package.pk)

        versions = []
        dated = []

        for release in releases:
            normalized = verlib.suggest_normalized_version(release.version)
            if normalized is not None:
                versions.append(release)
            else:
                dated.append(release)

        versions.sort(key=lambda x: verlib.NormalizedVersion(verlib.suggest_normalized_version(x.version)))
        dated.sort(key=lambda x: x.created)

        for i, release in enumerate(dated + versions):
            if release.order != i:
                Release.objects.filter(pk=release.pk).update(order=i)


@receiver(post_save, sender=Package)
def update_packages(sender, **kwargs):
    instance = kwargs.get("instance")
    if instance is not None:
        if kwargs.get("created", False):
            ChangeLog.objects.create(type=ChangeLog.TYPES.new, package=instance)


@receiver(post_save, sender=Release)
def release_changelog(sender, **kwargs):
    instance = kwargs.get("instance")
    if instance is not None:
        if kwargs.get("created", False):
            diff = instance.created - instance.package.created
            if diff.days != 0 or diff.seconds > 600:
                ChangeLog.objects.create(type=ChangeLog.TYPES.updated, package=instance.package, release=instance)
