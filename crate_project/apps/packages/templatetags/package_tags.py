from django import template
from django.db.models import F, Sum

from packages.models import Package, Release, ReleaseFile, ChangeLog

register = template.Library()


@register.assignment_tag
def package_download_count(package_name=None):
    # @@@ Cache this to cut down on queries
    count = 0
    if package_name is None:
        # Total Download Count
        count = ReleaseFile.objects.all().aggregate(total_downloads=Sum("downloads")).get("total_downloads", 0)
    else:
        count = ReleaseFile.objects.filter(
                    release__package__name=package_name
                ).aggregate(total_downloads=Sum("downloads")).get("total_downloads", 0)
    return count


@register.assignment_tag
def package_count():
    # @@@ Cache this to cut down on queries
    return Package.objects.all().count()


@register.assignment_tag
def get_oldest_package():
    # @@@ Cache this to cut down on queries
    pkgs = Package.objects.all().order_by("created")[:1]
    if pkgs:
        return pkgs[0]
    else:
        return None


@register.assignment_tag
def new_packages(num):
    return [
        x for
        x in ChangeLog.objects.filter(type=ChangeLog.TYPES.new).select_related("package", "release").prefetch_related("package__releases").order_by("-created")[:num * 3]
        if len(x.package.releases.all())
    ][:num]


@register.assignment_tag
def updated_packages(num):
    return ChangeLog.objects.filter(type=ChangeLog.TYPES.updated).select_related("package", "release").order_by("-created")[:num]


@register.assignment_tag
def featured_packages(num):
    return Package.objects.filter(featured=True).order_by("?")[:num]


@register.assignment_tag
def random_packages(num):
    return Package.objects.exclude(releases=None).order_by("?")[:num]


@register.assignment_tag
def package_versions(package_name, num=None):
    qs = Release.objects.filter(package__name=package_name).select_related("package").order_by("-order")
    if num is not None:
        qs = qs[:num]
    return qs


@register.assignment_tag
def package_version_count(package_name):
    return Release.objects.filter(package__name=package_name).count()
