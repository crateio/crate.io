from django.core.management.base import BaseCommand

from packages.models import Release, ReleaseFile


class Command(BaseCommand):

    def handle(self, *args, **options):
        Release.objects.filter(hidden=True).update(hidden=False)
        ReleaseFile.objects.filter(hidden=True).update(hidden=False)
