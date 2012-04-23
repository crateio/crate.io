import datetime
import os
import posixpath
import re
import urlparse
import uuid
import cStringIO
import sys

import bleach
import jinja2
import lxml.html

from docutils.core import publish_string, publish_parts
from docutils.utils import SystemMessage


from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.encoding import smart_str, force_unicode
from django.utils.importlib import import_module
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from model_utils.models import TimeStampedModel

from crate.fields import JSONField
from crate.utils.datatools import track_data
from packages.evaluators import ReleaseEvaluator
from packages.utils import verlib

ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
                    "br", "img", "span", "div", "pre", "p",
                    "dl", "dd", "dt", "tt", "cite",
                    "h1", "h2", "h3", "h4", "h5", "h6",
                    "table", "col", "tr", "td", "th", "tbody", "thead",
                    "colgroup",
                ]

ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES.items())
ALLOWED_ATTRIBUTES.update({
    "img": ["src"],
})

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
    normalized_name = models.SlugField(max_length=150, unique=True)
    downloads_synced_on = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.normalized_name = re.sub('[^A-Za-z0-9.]+', '-', self.name).lower()
        return super(Package, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"package": self.name})

    def get_simple_url(self):
        return reverse("simple_package_detail", kwargs={"slug": self.name})

    @property
    def downloads(self):
        KEY = "crate:packages:package:%s:downloads" % self.pk

        total_downloads = cache.get(KEY)
        if total_downloads is None:
            total_downloads = ReleaseFile.objects.filter(release__package=self).aggregate(total_downloads=Sum("downloads"))["total_downloads"]
            if total_downloads is None:
                total_downloads = 0

            cache.set(KEY, total_downloads)
        return total_downloads

    @property
    def latest(self):
        if not hasattr(self, "_latest_release"):
            releases = self.releases.filter(hidden=False).order_by("-order")[:1]
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

    @property
    def history(self):
        from history.models import Event

        return Event.objects.filter(package=self.package.name).order_by("-created")


class PackageURI(models.Model):
    package = models.ForeignKey(Package, related_name="package_links")
    uri = models.URLField(max_length=400)

    class Meta:
        unique_together = ["package", "uri"]

    def __unicode__(self):
        return self.uri


@track_data("hidden")
class Release(models.Model, ReleaseEvaluator):

    created = AutoCreatedField("created", db_index=True)
    modified = AutoLastModifiedField("modified")

    package = models.ForeignKey(Package, related_name="releases")
    version = models.CharField(max_length=512)

    hidden = models.BooleanField(default=False)
    show_install_command = models.BooleanField(default=True)

    order = models.IntegerField(default=0, db_index=True)

    platform = models.TextField(blank=True)

    summary = models.TextField(blank=True)
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

        super(Release, self).save(*args, **kwargs)

        _current_show_install_command = self.show_install_command

        if self.classifiers.filter(trove="Framework :: Plone").exists():
            self.show_install_command = False
        else:
            self.show_install_command = True

        if _current_show_install_command != self.show_install_command:
            super(Release, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"package": self.package.name, "version": self.version})

    @property
    def downloads(self):
        KEY = "crate:packages:release:%s:downloads" % self.pk

        total_downloads = cache.get(KEY)

        if total_downloads is None:
            total_downloads = self.files.aggregate(total_downloads=Sum("downloads"))["total_downloads"]
            if total_downloads is None:
                total_downloads = 0
            cache.set(KEY, total_downloads)

        return total_downloads

    @property
    def install_command(self):
        return "pip install %(package)s==%(version)s" % {"package": self.package.name, "version": self.version}

    @property
    def requirement_line(self):
        return "%(package)s==%(version)s" % {"package": self.package.name, "version": self.version}

    @property
    def description_html(self):
        if not hasattr(self, "_description_html"):
            # @@@ Consider Saving This to the DB
            docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
            docutils_settings.update({
                            "raw_enabled": 0,  # no raw HTML code
                            "file_insertion_enabled": 0,  # no file/URL access
                            "halt_level": 2,  # at warnings or errors, raise an exception
                            "report_level": 5,  # never report problems with the reST code
                        })

            old_stderr = sys.stderr
            sys.stderr = s = cStringIO.StringIO()

            msg = ""

            try:
                bits = self.description.split(".. :changelog:", 1)
                description = bits[0]
                parts = publish_parts(source=smart_str(description), writer_name="html4css1", settings_overrides=docutils_settings)
            except SystemMessage:
                msg = None
            else:
                if parts is None or len(s.getvalue()) > 0:
                    msg = None
                else:
                    cnt = force_unicode(parts["fragment"])
                    cnt = bleach.clean(cnt, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
                    cnt = bleach.linkify(cnt, skip_pre=True, parse_email=True)

                    msg = jinja2.Markup(cnt)

            sys.stderr = old_stderr
            self._description_html = msg

        return self._description_html

    @property
    def changelog_html(self):
        if not hasattr(self, "_changelog_html"):
            docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
            docutils_settings.update({
                            "raw_enabled": 0,  # no raw HTML code
                            "file_insertion_enabled": 0,  # no file/URL access
                            "halt_level": 2,  # at warnings or errors, raise an exception
                            "report_level": 5,  # never report problems with the reST code
                        })

            old_stderr = sys.stderr
            sys.stderr = s = cStringIO.StringIO()

            msg = ""

            try:
                bits = self.description.split(".. :changelog:", 1)

                if len(bits) > 1:
                    changelog = bits[1]
                else:
                    self._changelog_html = None
                    return

                parts = publish_parts(source=smart_str(changelog), writer_name="html4css1", settings_overrides=docutils_settings)
            except SystemMessage:
                msg = None
            else:
                if parts is None or len(s.getvalue()) > 0:
                    msg = None
                else:
                    cnt = force_unicode(parts["fragment"])
                    cnt = bleach.clean(cnt, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
                    cnt = bleach.linkify(cnt, skip_pre=True, parse_email=True)

                    msg = jinja2.Markup(cnt)

            sys.stderr = old_stderr
            self._changelog_html = msg

        return self._changelog_html


@track_data("hidden")
class ReleaseFile(models.Model):

    TYPES = Choices(
        ("sdist", _("Source")),
        ("bdist_egg", "Egg"),
        ("bdist_msi", "MSI"),
        ("bdist_dmg", "DMG"),
        ("bdist_rpm", "RPM"),
        ("bdist_dumb", _("Dumb Binary Distribution")),
        ("bdist_wininst", _("Windows Installer Binary Distribution")),
    )

    created = AutoCreatedField("created", db_index=True)
    modified = AutoLastModifiedField("modified")

    hidden = models.BooleanField(default=False)

    release = models.ForeignKey(Release, related_name="files")

    type = models.CharField(max_length=25, choices=TYPES)
    file = models.FileField(upload_to=release_file_upload_to, storage=package_storage, max_length=512, blank=True)
    filename = models.CharField(max_length=200, help_text="This is the file name given to us by PyPI", blank=True, null=True, default=None)
    digest = models.CharField(max_length=512, blank=True)

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
    version = models.CharField(max_length=50, blank=True)

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
    version = models.CharField(max_length=50, blank=True)

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
    version = models.CharField(max_length=50, blank=True)

    environment = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class DownloadDelta(models.Model):

    file = models.ForeignKey(ReleaseFile, related_name="download_deltas")
    date = models.DateField(default=datetime.date.today, db_index=True)
    delta = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Download Delta"
        verbose_name_plural = "Download Deltas"

        unique_together = ("file", "date")


class ChangeLog(models.Model):

    TYPES = Choices(
        ("new", "New"),
        ("updated", "Updated"),
    )

    created = AutoCreatedField("created", db_index=True)
    modified = AutoLastModifiedField("modified")

    type = models.CharField(max_length=25, choices=TYPES, db_index=True)
    package = models.ForeignKey(Package)
    release = models.ForeignKey(Release, blank=True, null=True)


class ReadTheDocsPackageSlug(models.Model):
    package = models.OneToOneField(Package, related_name="readthedocs_slug")
    slug = models.CharField(max_length=150, unique=True)

    def __unicode__(self):
        return u"%s" % self.slug


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


@receiver(post_save, sender=Package)
@receiver(post_delete, sender=Package)
def regenerate_simple_index(sender, **kwargs):
    from packages.tasks import refresh_package_index_cache
    refresh_package_index_cache.delay()
