from django.conf.urls import patterns, url

from pypi.simple.views import PackageIndex, PackageDetail

handler404 = "pypi.simple.views.not_found"

urlpatterns = patterns("",
    url(r"^simple/$", PackageIndex.as_view(), name="pypi_package_index"),
    url(r"^simple/(?P<slug>[^/]+)/$", PackageDetail.as_view(), name="pypi_package_detail"),
)
