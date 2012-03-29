from django.conf.urls import url

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.cache import SimpleCache
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from packages.models import Package, Release, ReleaseFile, ReleaseURI, TroveClassifier
from packages.models import ReleaseRequire, ReleaseProvide, ReleaseObsolete


class InlineTroveClassifierResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["trove"]
        filtering = {
            "trove": ALL,
        }
        include_resource_uri = False
        ordering = ["trove"]
        queryset = TroveClassifier.objects.all()
        resource_name = "classifier"


class PackageResource(ModelResource):
    releases = fields.ToManyField("packages.api.ReleaseResource", "releases")
    downloads = fields.IntegerField("downloads")
    latest = fields.ToOneField("packages.api.InlineReleaseResource", "latest", full=True)

    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["created", "downloads_synced_on", "downloads", "name"]
        filtering = {
            "name": ALL,
            "created": ALL,
            "downloads_synced_on": ALL,
        }
        include_absolute_url = True
        ordering = ["created", "downloads_synced_on"]
        queryset = Package.objects.all()
        resource_name = "package"

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>[^/]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("dispatch_detail"), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            "resource_name": self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs["name"] = bundle_or_obj.obj.name
        else:
            kwargs["name"] = bundle_or_obj.name

        if self._meta.api_name is not None:
            kwargs["api_name"] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)


class InlineReleaseResource(ModelResource):
    files = fields.ToManyField("packages.api.ReleaseFileResource", "files", full=True)
    uris = fields.ToManyField("packages.api.ReleaseURIResource", "uris", full=True)
    classifiers = fields.ListField()
    requires = fields.ToManyField("packages.api.ReleaseRequireResource", "requires", full=True)
    provides = fields.ToManyField("packages.api.ReleaseProvideResource", "provides", full=True)
    obsoletes = fields.ToManyField("packages.api.ReleaseObsoleteResource", "obsoletes", full=True)
    downloads = fields.IntegerField("downloads")

    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = [
                    "author", "author_email", "created", "description", "download_uri", "downloads",
                    "license", "maintainer", "maintainer_email", "package", "platform", "classifiers",
                    "requires_python", "summary", "version"
                ]
        include_absolute_url = True
        include_resource_uri = False
        queryset = Release.objects.all()


class ReleaseResource(ModelResource):
    package = fields.ForeignKey(PackageResource, "package")
    files = fields.ToManyField("packages.api.ReleaseFileResource", "files", full=True)
    uris = fields.ToManyField("packages.api.ReleaseURIResource", "uris", full=True)
    classifiers = fields.ListField()
    requires = fields.ToManyField("packages.api.ReleaseRequireResource", "requires", full=True)
    provides = fields.ToManyField("packages.api.ReleaseProvideResource", "provides", full=True)
    obsoletes = fields.ToManyField("packages.api.ReleaseObsoleteResource", "obsoletes", full=True)
    downloads = fields.IntegerField("downloads")

    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = [
                    "author", "author_email", "created", "description", "download_uri", "downloads",
                    "license", "maintainer", "maintainer_email", "package", "platform", "classifiers",
                    "requires_python", "summary", "version"
                ]
        filtering = {
            "author": ALL,
            "author_email": ALL,
            "maintainer": ALL,
            "maintainer_email": ALL,
            "created": ALL,
            "license": ALL,
            "version": ALL,
        }
        include_absolute_url = True
        ordering = ["created", "license", "package", "version"]
        queryset = Release.objects.all()
        resource_name = "release"

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<package__name>[^/]+)-(?P<version>[^/]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("dispatch_detail"), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            "resource_name": self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs["package__name"] = bundle_or_obj.obj.package.name
            kwargs["version"] = bundle_or_obj.obj.version
        else:
            kwargs["name"] = bundle_or_obj.package.name
            kwargs["version"] = bundle_or_obj.version

        if self._meta.api_name is not None:
            kwargs["api_name"] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def dehydrate_classifiers(self, bundle):
        return [c.trove for c in bundle.obj.classifiers.all()]


class ReleaseFileResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["comment", "created", "digest", "downloads", "file", "filename", "python_version", "type"]
        include_resource_uri = False
        queryset = ReleaseFile.objects.all()
        resource_name = "files"


class ReleaseURIResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["label", "uri"]
        include_resource_uri = False
        queryset = ReleaseURI.objects.all()
        resource_name = "uris"


class ReleaseRequireResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["kind", "name", "version", "environment"]
        include_resource_uri = False
        queryset = ReleaseRequire.objects.all()
        resource_name = "requires"


class ReleaseProvideResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["kind", "name", "version", "environment"]
        include_resource_uri = False
        queryset = ReleaseProvide.objects.all()
        resource_name = "provides"


class ReleaseObsoleteResource(ModelResource):
    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["kind", "name", "version", "environment"]
        include_resource_uri = False
        queryset = ReleaseObsolete.objects.all()
        resource_name = "obsoletes"
