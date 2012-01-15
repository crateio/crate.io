from haystack import indexes

from packages.models import Package

# @@@ We should provide some sort of boost from the downloads field
#       (something with an order of magnitude more downloads is probably better)
# @@@ Should We Filter Out Packages With No Releases?


class PackageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name", boost=1.5)
    summary = indexes.CharField(model_attr="summary", null=True)

    downloads = indexes.IntegerField(model_attr="downloads", indexed=False)
    url = indexes.CharField(model_attr="get_absolute_url", indexed=False)

    def get_model(self):
        return Package

    def prepare(self, obj):
        data = super(PackageIndex, self).prepare(obj)
        # We want to scale the boost for this document based on how many downloads have
        #   been recorded for this package.

        # @@@ Might want to actually tier these values instead of percentage them.
        # Cap out downloads at 100k
        capped_downloads = min(data["downloads"], 10000)
        boost = capped_downloads / 10000.0

        # @@@ Is 2 too high of a maximum boost?
        data["_boost"] = 1.0 + boost

        return data
