from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect


def simple_redirect(request, path=None):
    host = settings.SIMPLE_API_URL

    if path is not None:
        if not path.startswith("/"):
            path = "/" + path

        redirect_to = urljoin(host, path)
    else:
        redirect_to = host
    return HttpResponseRedirect(redirect_to)
