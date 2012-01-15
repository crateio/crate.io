import datetime

from django import template
from django.db.models import F, Sum

from packages.models import Package, Release, ReleaseFile

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
def new_releases(num):
    return Release.objects.all().order_by("-created").select_related("package")[:num]


@register.assignment_tag
def updated_releases(num):
    return [x.release for x in ReleaseFile.objects.exclude(created=F("release__created")).order_by("-created")[:num]]
