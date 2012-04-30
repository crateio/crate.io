from django.conf.urls import patterns, url

from lists.views import RemoveFromList

urlpatterns = patterns("",
    url(r"^(?P<list>[^/]+)/(?P<package>[^/]+)/remove/$", RemoveFromList.as_view(), name="remove_package_from_list")
)
