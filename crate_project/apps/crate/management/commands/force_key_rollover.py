from django.core.management.base import BaseCommand
from pypi.tasks import pypi_key_rollover


class Command(BaseCommand):

    def handle(self, *args, **options):
        pypi_key_rollover.delay()
