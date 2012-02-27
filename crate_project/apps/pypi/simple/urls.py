from django.conf.urls import patterns, url

from pypi.simple.views import PackageDetail, PackageServerSig

handler404 = "pypi.simple.views.not_found"

urlpatterns = patterns("",
    url(r"^$", "pypi.simple.views.simple_redirect"),
    url(r"^simple/$", "pypi.simple.views.package_index", name="pypi_package_index"),
    url(r"^simple/(?P<slug>[^/]+)/$", PackageDetail.as_view(), name="pypi_package_detail"),
    url(r"^packages/.+/(?P<filename>[^/]+)/$", "pypi.simple.views.file_redirect", name="pypi_file_redirect"),
    url(r"^serversig/(?P<slug>[^/]+)/$", PackageServerSig.as_view()),
    url(r"^last-modified/", "pypi.simple.views.last_modified"),
)
