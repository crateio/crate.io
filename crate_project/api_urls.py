from django.conf.urls import patterns, include, url

from tastypie.api import Api

from packages.api import PackageResource, ReleaseResource

v1_api = Api(api_name="v1")

v1_api.register(PackageResource())
v1_api.register(ReleaseResource())


urlpatterns = patterns("",
    url("", include(include(v1_api.urls))),
)
