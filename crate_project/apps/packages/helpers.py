from django.db.models import Sum

from jingo import register
from packages.models import Package, ReleaseFile

@register.function
def package_information():
    return {
        "downloads": ReleaseFile.objects.all().aggregate(total_downloads=Sum("downloads")).get("total_downloads", 0),
        "packages": Package.objects.all().count(),
    }
