from celery.task import task

from packages.models import Release


@task
def save_releases(releases):
    for r in Release.objects.filter(pk__in=releases):
        r.save()
