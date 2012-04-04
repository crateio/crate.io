from django.utils.translation import ugettext_noop as _

from haystack import indexes

from packages.models import Package
from search.indexes import PackageCelerySearchIndex

LICENSES = {
    "GNU General Public License (GPL)": "GPL",
    "GNU Library or Lesser General Public License (LGPL)": "LGPL",
    "GNU Affero General Public License v3": "Affero GPL",
    "Apache Software License": "Apache License",
    "ISC License (ISCL)": "ISC License",
    "Other/Proprietary License": _("Other/Proprietary"),
}


class PackageIndex(PackageCelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name", boost=1.5)
    summary = indexes.CharField(null=True)
    description = indexes.CharField(null=True)
    author = indexes.CharField(null=True)
    maintainer = indexes.CharField(null=True)
    downloads = indexes.IntegerField(model_attr="downloads", indexed=False)
    url = indexes.CharField(model_attr="get_absolute_url", indexed=False)
    operating_systems = indexes.MultiValueField(null=True, faceted=True, facet_class=indexes.FacetMultiValueField)
    licenses = indexes.MultiValueField(null=True, faceted=True, facet_class=indexes.FacetMultiValueField)
    implementations = indexes.MultiValueField(null=True, faceted=True, facet_class=indexes.FacetMultiValueField)
    python_versions = indexes.MultiValueField(null=True, faceted=True, facet_class=indexes.FacetMultiValueField)
    versions = indexes.MultiValueField(null=True)
    release_count = indexes.IntegerField(default=0)

    def get_model(self):
        return Package

    def prepare(self, obj):
        data = super(PackageIndex, self).prepare(obj)

        # For ES, because it doesn't tokenize on ``_``, which causes problems
        # on lots of searches.
        if '_' in data['name']:
            data['name'] += ' ' + data['name'].replace('_', '-')

        if obj.latest:
            data["summary"] = obj.latest.summary
            data["author"] = obj.latest.author if obj.latest.author else None
            data["maintainer"] = obj.latest.maintainer if obj.latest.maintainer else None
            data["description"] = obj.latest.description if obj.latest.description else None

            operating_systems = []
            licenses = []
            implementations = []
            python_versions = []

            for classifier in obj.latest.classifiers.all():
                if classifier.trove.startswith("License ::"):
                    # We Have a License for This Project
                    licenses.append(classifier.trove.rsplit("::", 1)[1].strip())
                elif classifier.trove.startswith("Operating System ::"):
                    operating_systems.append(classifier.trove.rsplit("::", 1)[1].strip())
                elif classifier.trove.startswith("Programming Language :: Python :: Implementation ::"):
                    implementations.append(classifier.trove.rsplit("::", 1)[1].strip())
                elif classifier.trove.startswith("Programming Language :: Python ::"):
                    if classifier.trove == "Programming Language :: Python :: 2 :: Only":
                        python_versions.append("2.x")
                    elif classifier.trove.startswith("Programming Language :: Python :: 2"):
                        python_versions.append("2.x")
                    elif classifier.trove.startswith("Programming Language :: Python :: 3"):
                        python_versions.append("3.x")
                    else:
                        python_versions.append(classifier.trove.rsplit("::", 1)[1].strip())

            if not licenses:
                licenses = [_("Unknown")]

            licenses = [x for x in licenses if x not in ["OSI Approved"]]
            licenses = [LICENSES.get(x, x) for x in licenses]

            data["licenses"] = licenses

            if not operating_systems:
                operating_systems = [_("Unknown")]
            data["operating_systems"] = operating_systems

            if not implementations:
                implementations = [_("Unknown")]
            data["implementations"] = implementations

            if not python_versions:
                python_versions = [_("Unknown")]
            data["python_versions"] = python_versions

        # Pack in all the versions in decending order.
        releases = obj.releases.all().order_by("-order")
        data["versions"] = [release.version for release in releases if release.version]
        data["release_count"] = releases.count()

        # We want to scale the boost for this document based on how many downloads have
        #   been recorded for this package.
        # @@@ Might want to actually tier these values instead of percentage them.
        # Cap out downloads at 100k
        capped_downloads = min(data["downloads"], 10000)
        boost = capped_downloads / 10000.0
        data["_boost"] = 1.0 + boost

        return data
