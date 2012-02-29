from django.conf import settings

from django_hosts import patterns, host

host_patterns = patterns("",
    host(r"www", settings.ROOT_URLCONF, name="default"),
    host(r"simple", "packages.simple.urls", name="simple"),
    host(r"pypi", "pypi.simple.urls", name="pypi"),
    host(r"restricted", "packages.simple.restricted_urls", name="restricted"),
)
