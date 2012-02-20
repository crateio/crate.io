from django.core.management.base import BaseCommand

from packages.models import ReleaseFile
from pypi.processor import PyPIPackage


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for rf in ReleaseFile.objects.filter(digest="").distinct("release__package"):
            p = PyPIPackage(rf.release.package)
            p.process()
            i += 1
            print rf.release.package.name, rf.release.version
        print "Fixed %d packages" % i
