import re

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect, Http404
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from packages.models import Package


def not_found(request):
    return HttpResponseNotFound("Not Found")


class PackageIndex(ListView):

    restricted = False
    queryset = Package.objects.all().order_by("name")
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


class PackageDetail(DetailView):

    restricted = False
    queryset = Package.objects.all().prefetch_related("releases__uris", "releases__files", "package_links")
    slug_field = "name__iexact"
    template_name = "packages/simple/package_detail.html"

    def get_object(self, queryset=None):
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            try:
                queryset = self.get_queryset()
                queryset = queryset.filter(normalized_name=re.sub('[^A-Za-z0-9.]+', '-', slug).lower())
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        return obj

    def get_context_data(self, **kwargs):
        ctx = super(PackageDetail, self).get_context_data(**kwargs)

        releases = self.object.releases.all()

        if self.kwargs.get("version"):
            releases = releases.filter(version=self.kwargs["version"])
        else:
            releases = releases.filter(hidden=False)

        ctx.update({
            "releases": releases,
            "restricted": self.restricted,
            "show_hidden": True if self.kwargs.get("version") else False,
        })

        return ctx

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("simple_package_detail", kwargs={"slug": self.object.name}))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
