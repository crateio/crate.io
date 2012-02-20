import redis

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = redis.StrictRedis(**getattr(settings, "PYPI_DATASTORE_CONFIG", {}))
        if args:
            r.set("crate:pypi:since", args[0])
