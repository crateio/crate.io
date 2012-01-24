from django.conf.urls import patterns, url

from search.views import Search


urlpatterns = patterns("",
    url(r"^$", Search.as_view(), name="search"),
)
