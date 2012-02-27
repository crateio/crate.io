import base64
import datetime
import logging

import redis
import requests

from django.conf import settings
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
from pypi.models import PyPIMirrorPage, PyPIServerSigPage, PyPIIndexPage

PYPI_SINCE_KEY = "crate:pypi:since"

logger = logging.getLogger(__name__)


def not_found(request):
    return HttpResponseNotFound("Not Found")


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


#@cache_page(60 * 15)
def last_modified(request):
    datastore = redis.StrictRedis(**getattr(settings, "PYPI_DATASTORE_CONFIG", {}))
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
