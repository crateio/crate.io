from django.conf.urls import patterns, url

from packages.views import PackageDetail, ReleaseDetail

urlpatterns = patterns("",
    url(r"^(?P<name>[^/]+)/$", PackageDetail.as_view(), name="package_detail"),
    url(r"^(?P<name>[^/]+)/(?P<version>[^/]+)/$", ReleaseDetail.as_view(), name="release_detail"),
)
