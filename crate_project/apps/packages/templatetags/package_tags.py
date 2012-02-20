from django import template
from django.core.cache import cache
from django.db.models import Sum

from packages.models import Package, Release, ReleaseFile, ChangeLog

register = template.Library()


@register.assignment_tag
def package_download_count(package_name=None):
    if package_name is None:
        cached = cache.get("crate:stats:download_count")

        if cached:
            return cached

        count = ReleaseFile.objects.all().aggregate(total_downloads=Sum("downloads")).get("total_downloads", 0)
        cache.set("crate:stats:download_count", count, 60 * 60)
        return count
    else:
        cached = cache.get("crate:stats:download_count:%s" % package_name)

        if cached:
            return cached

        count = ReleaseFile.objects.filter(
                    release__package__name=package_name
                ).aggregate(total_downloads=Sum("downloads")).get("total_downloads", 0)
        cache.set("crate:stats:download_count:%s" % package_name, count, 60 * 60 * 24)
        return count


@register.assignment_tag
def package_count():
    cached = cache.get("crate:stats:package_count")

    if cached:
        return cached

    count = Package.objects.all().count()
    cache.set("crate:stats:package_count", count, 60 * 60)
    return count


@register.assignment_tag
def get_oldest_package():
    cached = cache.get("crate:stats:oldest_package")

    if cached:
        return cached

    pkgs = Package.objects.all().order_by("created")[:1]

    if pkgs:
        cache.set("crate:stats:oldest_package", pkgs[0], 60 * 60 * 24 * 7)
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
    return ChangeLog.objects.filter(type=ChangeLog.TYPES.updated).select_related("package", "release", "release__package").order_by("-created")[:num]


@register.assignment_tag
def featured_packages(num):
    return Package.objects.filter(featured=True).order_by("?")[:num]


@register.assignment_tag
def random_packages(num):
    return Package.objects.exclude(releases=None).order_by("?")[:num]


@register.assignment_tag
def package_versions(package_name, num=None):
    qs = Release.objects.filter(package__name=package_name, deleted=False).select_related("package").order_by("-order")
    if num is not None:
        qs = qs[:num]
    return qs


@register.assignment_tag
def package_version_count(package_name):
    return Release.objects.filter(package__name=package_name).count()
