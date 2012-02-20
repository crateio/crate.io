import redis

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = redis.StrictRedis(host=settings.GONDOR_REDIS_HOST, port=settings.GONDOR_REDIS_PORT, password=settings.GONDOR_REDIS_PASSWORD)
        r.delete("celery")
