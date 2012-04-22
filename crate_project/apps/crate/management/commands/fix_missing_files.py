from django.core.management.base import BaseCommand

from packages.models import ReleaseFile
from pypi.processor import PyPIPackage


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for rf in ReleaseFile.objects.filter(digest="").distinct("release")[:10]:
            print rf.release.package.name, rf.release.version
            p = PyPIPackage(rf.release.package.name, version=rf.release.version)
            p.process(skip_modified=False)
            i += 1
        print "Fixed %d releases" % i
