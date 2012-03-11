from django.conf.urls import patterns, url

from packages.simple.views import PackageIndex, PackageDetail

handler404 = "packages.simple.views.not_found"

urlpatterns = patterns("",
    url(r"^$", PackageIndex.as_view(), name="simple_package_index"),
    url(r"^(?P<slug>[^/]+)/(?:(?P<version>[^/]+)/)?$", PackageDetail.as_view(), name="simple_package_detail"),
)
