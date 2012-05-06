import collections
import datetime

import redis

from django.conf import settings
from django.utils.timezone import utc

from admin_tools.dashboard.modules import DashboardModule


class StatusModule(DashboardModule):

    title = "Status"
    template = "admin_tools/dashboard/modules/status.html"

    def init_with_context(self, context):
        if hasattr(settings, "PYPI_DATASTORE"):
            datastore = redis.StrictRedis(**dict([(x.lower(), y) for x, y in settings.REDIS[settings.PYPI_DATASTORE].items()]))

            if datastore.get("crate:pypi:since") is not None:
                self.last_sync = datetime.datetime.fromtimestamp(float(datastore.get("crate:pypi:since")))
                self.last_sync.replace(tzinfo=utc)
            else:
                self.last_sync = None

            self.celery_queue_length = datastore.llen("celery")

    def is_empty(self):
        return False


class RedisStatusModule(DashboardModule):

    title = "Redis Status"
    template = "admin_tools/dashboard/modules/redis.html"

    def init_with_context(self, context):
        if hasattr(settings, "PYPI_DATASTORE"):
            datastore = redis.StrictRedis(**dict([(x.lower(), y) for x, y in settings.REDIS[settings.PYPI_DATASTORE].items()]))
            self.redis_info = collections.OrderedDict(sorted([(k, v) for k, v in datastore.info().iteritems()], key=lambda x: x[0]))

    def is_empty(self):
        return False
