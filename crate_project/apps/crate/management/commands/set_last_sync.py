import redis

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = redis.StrictRedis(**dict([(x.lower(), y) for x, y in settings.REDIS[settings.PYPI_DATASTORE].items()]))
        if args:
            r.set("crate:pypi:since", args[0])
