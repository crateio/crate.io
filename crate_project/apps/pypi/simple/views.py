import base64

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from crate.template2 import env

from packages.models import ReleaseFile
from pypi.models import PyPIMirrorPage, PyPIServerSigPage


def not_found(request):
    return HttpResponseNotFound("Not Found")


class PackageIndex(ListView):

    queryset = PyPIMirrorPage.objects.all().select_related("package").order_by("package__name")
    template_name = "pypi/simple/package_list.html"

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super(PackageIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self, force_uncached=False):
        cached = cache.get("crate:pypi:simple:PackageIndex:queryset")

        if cached and not force_uncached:
            return cached

        qs = super(PackageIndex, self).get_queryset()
        cache.set("crate:pypi:simple:PackageIndex:queryset", list(qs), 60 * 60 * 24 * 365)
        return qs

    def render_to_response(self, context, **response_kwargs):
        t = env.select_template(self.get_template_names())
        return HttpResponse(t.render(request=self.request, **context))


class PackageDetail(DetailView):
    queryset = PyPIMirrorPage.objects.all()
    slug_field = "package__name__iexact"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.package.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("pypi_package_detail", kwargs={"slug": self.object.package.name}))

        return HttpResponse(self.object.content)


class PackageServerSig(DetailView):
    queryset = PyPIServerSigPage.objects.all()
    slug_field = "package__name__iexact"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.package.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("pypi_package_detail", kwargs={"slug": self.object.package.name}))

        return HttpResponse(base64.b64decode(self.object.content), mimetype="application/octet-stream")


def file_redirect(request, filename):
    release_file = get_object_or_404(ReleaseFile, filename=filename)
    return HttpResponsePermanentRedirect(release_file.file.url)


def simple_redirect(request):
    return HttpResponsePermanentRedirect(reverse("pypi_package_index"))
