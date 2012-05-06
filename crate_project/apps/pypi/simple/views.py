import base64
import datetime
import logging
import re

import redis
import requests

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView

from packages.models import ReleaseFile
from pypi.models import PyPIMirrorPage, PyPIServerSigPage, PyPIIndexPage

PYPI_SINCE_KEY = "crate:pypi:since"

logger = logging.getLogger(__name__)


def not_found(request):
    return HttpResponseNotFound("Not Found")


class PackageDetail(DetailView):
    queryset = PyPIMirrorPage.objects.all()
    slug_field = "package__name__iexact"

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
                queryset = queryset.filter(package__normalized_name=re.sub('[^A-Za-z0-9.]+', '-', slug).lower())
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.package.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("pypi_package_detail", kwargs={"slug": self.object.package.name}))

        return HttpResponse(self.object.content)


class PackageServerSig(DetailView):
    queryset = PyPIServerSigPage.objects.all()
    slug_field = "package__name__iexact"

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
                queryset = queryset.filter(package__normalized_name=re.sub('[^A-Za-z0-9.]+', '-', slug).lower())
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check that the case matches what it's supposed to be
        if self.object.package.name != self.kwargs.get(self.slug_url_kwarg, None):
            return HttpResponsePermanentRedirect(reverse("pypi_package_serversig", kwargs={"slug": self.object.package.name}))

        return HttpResponse(base64.b64decode(self.object.content), mimetype="application/octet-stream")


@cache_page(60 * 15)
def package_index(request, force_uncached=False):
    idx = PyPIIndexPage.objects.all().order_by("-created")[:1]

    if idx and not force_uncached:
        return HttpResponse(idx[0].content)
    else:
        try:
            r = requests.get("http://pypi.python.org/simple/", prefetch=True)
            idx = PyPIIndexPage.objects.create(content=r.content)
            return HttpResponse(idx.content)
        except Exception:
            logger.exception("Error trying to Get New Simple Index")

            idx = PyPIIndexPage.objects.all().order_by("-created")[:1]

            if idx:
                return HttpResponse(idx[0].content)  # Serve Stale Cache
            raise


def last_modified(request):
    datastore = redis.StrictRedis(**dict([(x.lower(), y) for x, y in settings.REDIS[settings.PYPI_DATASTORE].items()]))
    ts = datastore.get(PYPI_SINCE_KEY)
    if ts is not None:
        dt = datetime.datetime.utcfromtimestamp(int(float(ts)))
        return HttpResponse(dt.isoformat(), mimetype="text/plain")
    else:
        return HttpResponseNotFound("Never Synced")


def file_redirect(request, filename):
    release_file = get_object_or_404(ReleaseFile, filename=filename)
    return HttpResponsePermanentRedirect(release_file.file.url)


def simple_redirect(request):
    return HttpResponsePermanentRedirect(reverse("pypi_package_index"))
