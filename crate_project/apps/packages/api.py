from django.conf.urls import include, url

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.cache import SimpleCache
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from packages.models import Package, Release, ReleaseFile, ReleaseURI


class PackageResource(ModelResource):
    releases = fields.ToManyField("packages.api.ReleaseResource", "releases")

    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = ["created", "downloads_synced_on", "name"]
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


class ReleaseResource(ModelResource):
    package = fields.ForeignKey(PackageResource, "package")
    files = fields.ToManyField("packages.api.ReleaseFileResource", "files", full=True)
    uris = fields.ToManyField("packages.api.ReleaseURIResource", "uris", full=True)

    class Meta:
        allowed_methods = ["get"]
        cache = SimpleCache()
        fields = [
                    "author", "author_email", "created", "description", "download_uri",
                    "license", "maintainer", "maintainer_email", "package", "platform",
                    "requires_python", "summary", "version"
                ]
        include_absolute_url = True
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
