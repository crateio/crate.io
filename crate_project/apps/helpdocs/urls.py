from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^setting-up-pip/$", direct_to_template, {"template": "helpdocs/setting-up-pip.html"}, name="helpdocs_pip"),
)
