from celery.task import task

from packages.stats.views import fetch_stats
from packages.simple.views import PackageIndex
from packages.models import Package, DownloadStatsCache


@task
def refresh_package_index_cache():
    pi = PackageIndex()
    pi.get_queryset(force_uncached=True)


@task
def refresh_stats_cache(package_pk):
    package = Package.objects.get(pk=package_pk)

    try:
        obj = DownloadStatsCache.objects.get(package=package)
    except DownloadStatsCache.DoesNotExist:
        DownloadStatsCache.objects.create(package=package, data=fetch_stats(package))
    else:
        DownloadStatsCache.objects.filter(pk=obj.pk).update(data=fetch_stats(package))
