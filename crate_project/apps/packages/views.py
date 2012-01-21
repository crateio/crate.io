from django.views.generic.detail import DetailView

from packages.models import Package, Release


class PackageDetail(DetailView):

    model = Package
    slug_url_kwarg = "name"
    slug_field = "name"


class ReleaseDetail(DetailView):

    model = Release
    slug_url_kwarg = "version"
    slug_field = "version"

    def get_queryset(self):
        qs = super(ReleaseDetail, self).get_queryset()
        qs = qs.filter(package__name=self.kwargs["name"])
        return qs
