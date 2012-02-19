from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from packages.models import Package


def not_found(request):
    return HttpResponseNotFound("Not Found")


class PackageIndex(ListView):
    queryset = Package.objects.filter(deleted=False).order_by("name")
    template_name = "packages/simple/package_list.html"


class PackageDetail(DetailView):
    queryset = Package.objects.filter(deleted=False).prefetch_related("releases__uris", "releases__files", "package_links")
    slug_field = "name__iexact"
    template_name = "packages/simple/package_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super(PackageDetail, self).get_context_data(**kwargs)
        ctx.update({
            "releases": self.object.releases.filter(deleted=False),
        })
        return ctx

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("simple_package_detail", kwargs={"slug": self.object.name}))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
