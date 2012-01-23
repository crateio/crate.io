import os
import json

from django.conf import settings
from django.core.management.base import NoArgsCommand

from packages.models import TroveClassifier, Package, Release


class Command(NoArgsCommand):

    can_import_settings = True

    def handle_noargs(self, **options):
        fpath = os.path.join(settings.FIXTURE_DIRS[0], "release.json")
        with open(fpath, "r") as f:
            j = json.load(f)
            for m in j:
                # {"pk": 1, "model": "packages.troveclassifier", "fields": {"trove": "Development Status :: 1 - Planning"}}
                p = Package.objects.get(id=m["fields"].pop("package"))
                uris = eval(m["fields"].pop("uris"))
                raw_data = eval(m["fields"].pop("raw_data"))
                classifiers = TroveClassifier.objects.filter(pk__in=m["fields"].pop("classifiers"))
                r = Release(
                    id=m["pk"],
                    package=p,
                    uris=uris,
                    raw_data=raw_data,
                    **m["fields"]
                )
                for classifier in classifiers:
                    r.classifiers.add(classifier)
                r.save()
