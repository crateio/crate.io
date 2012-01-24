from django.conf.urls import patterns, url

from packages.simple.views import PackageIndex, PackageDetail

urlpatterns = patterns("",
    url(r"^$", PackageIndex.as_view(), name="simple_package_index"),
    url(r"^(?P<slug>.*)/$", PackageDetail.as_view(), name="simple_package_detail"),
)
