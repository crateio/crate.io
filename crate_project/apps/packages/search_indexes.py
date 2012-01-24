from haystack import indexes
from packages.models import Package


class PackageIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name", boost=1.5)
    summary = indexes.CharField(null=True)
    downloads = indexes.IntegerField(model_attr="downloads", indexed=False)
    url = indexes.CharField(model_attr="get_absolute_url", indexed=False)
    platform = indexes.CharField(null=True, faceted=True)
    license = indexes.CharField(null=True, faceted=True)
    versions = indexes.MultiValueField(null=True)
    release_count = indexes.IntegerField(default=0)
    modified = indexes.DateTimeField(model_attr='modified', faceted=True)

    def get_model(self):
        return Package

    def prepare(self, obj):
        data = super(PackageIndex, self).prepare(obj)
        # We want to scale the boost for this document based on how many downloads have
        #   been recorded for this package.

        if obj.latest:
            data['summary'] = obj.latest.summary
            data['platform'] = obj.latest.platform
            data['license'] = obj.latest.license

        # Pack in all the versions in decending order.
        releases = obj.releases.order_by('-created')
        data['versions'] = [release.version for release in releases if release.version]
        data['release_count'] = releases.count()

        # @@@ Might want to actually tier these values instead of percentage them.
        # Cap out downloads at 100k
        capped_downloads = min(data["downloads"], 10000)
        boost = capped_downloads / 10000.0
        data["_boost"] = 1.0 + boost

        return data
