from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponsePermanentRedirect
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from crate.template2 import env

from packages.models import Package


def not_found(request):
    return HttpResponseNotFound("Not Found")


class PackageIndex(ListView):
    queryset = Package.objects.filter(deleted=False).order_by("name")
    template_name = "packages/simple/package_list.html"

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super(PackageIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self, force_uncached=False):
        cached = cache.get("crate:packages:simple:PackageIndex:queryset")

        if cached and not force_uncached:
            return cached

        qs = super(PackageIndex, self).get_queryset()
        cache.set("crate:packages:simple:PackageIndex:queryset", list(qs), 60 * 60 * 24 * 365)
        return qs

    def render_to_response(self, context, **response_kwargs):
        t = env.select_template(self.get_template_names())
        return HttpResponse(t.render(request=self.request, **context))


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
