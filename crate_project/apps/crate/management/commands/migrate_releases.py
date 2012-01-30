from django.core.management.base import BaseCommand
from pypi.tasks import migrate_all_releases


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "Migrating All Releases"
        migrate_all_releases.delay()
