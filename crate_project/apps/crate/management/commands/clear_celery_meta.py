import redis

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = redis.StrictRedis(host=settings.GONDOR_REDIS_HOST, port=settings.GONDOR_REDIS_PORT, password=settings.GONDOR_REDIS_PASSWORD)
        i = 0
        for key in r.keys("celery-*"):
            r.delete(key)
            i += 1
        print "%d keys cleared" % i
