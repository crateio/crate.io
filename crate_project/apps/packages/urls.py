from django.conf.urls import patterns, url

from packages.views import PackageDetail

urlpatterns = patterns("",
    url(r"^(?P<name>.*)/$", PackageDetail.as_view(), name="package_detail"),
)
