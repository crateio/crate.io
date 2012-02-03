from tastypie import fields
from tastypie.resources import ModelResource

from packages.models import Package, Release


class PackageResource(ModelResource):
    releases = fields.ToManyField("packages.api.ReleaseResource", "releases")

    class Meta:
        queryset = Package.objects.all()
        resource_name = "package"


class ReleaseResource(ModelResource):
    package = fields.ForeignKey(PackageResource, "package")

    class Meta:
        queryset = Release.objects.all()
        resource_name = "release"
        fields = [
                    "author", "author_email", "created", "description", "download_uri",
                    "license", "maintainer", "maintainer_email", "package", "platform",
                    "requires_python", "summary", "version"
                ]
