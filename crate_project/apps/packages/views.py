from django.views.generic.detail import DetailView

from packages.models import Package


class PackageDetail(DetailView):

    model = Package
    slug_url_kwarg = "name"
    slug_field = "name"
