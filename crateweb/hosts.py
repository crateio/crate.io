from django.conf import settings

from django_hosts import patterns, host

host_patterns = patterns("",
    host(r"www", settings.ROOT_URLCONF, name="default"),
    host(r"simple", "crate.web.packages.simple.urls", name="simple"),
    host(r"pypi", "crate.pypi.simple.urls", name="pypi"),
    host(r"restricted", "crate.web.packages.simple.restricted_urls", name="restricted"),
)
