from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from packages.models import Package


class PackageIndex(ListView):
    queryset = Package.objects.all().order_by("name")
    template_name = "packages/simple/package_list.html"


class PackageDetail(DetailView):
    model = Package
    slug_field = "name"
    template_name = "packages/simple/package_detail.html"
