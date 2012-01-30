from django.core.management.base import BaseCommand

from pypi.models import TaskLog
from pypi import tasks


class Command(BaseCommand):

    def handle(self, *args, **options):
        for tl in TaskLog.objects.filter(status=TaskLog.STATUS.failed):
            t = getattr(tasks, tl.name, None)
            if t is not None:
                t.delay(*eval(t.args), **eval(t.kwargs))
                tl.status = TaskLog.STATUS.resubmitted
                tl.save()
