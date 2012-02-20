from django.core.management.base import BaseCommand

from pypi.tasks import bulk_synchronize


class Command(BaseCommand):

    def handle(self, *args, **options):
        bulk_synchronize.delay()
        print "Bulk Synchronize Triggered"
