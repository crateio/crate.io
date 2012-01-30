from optparse import make_option

from django.core.management.base import BaseCommand

from pypi.tasks import synchronize_mirror


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("--since",
            dest="since",
            default=-1),
        )

    def handle(self, *args, **options):
        if options.get("since", -1) == -1:
            since = None
        else:
            since = 0

        synchronize_mirror.delay(since=since)

        print "Done"
