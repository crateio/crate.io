from django.conf.urls import patterns, url

from favorites.views import ToggleFavorite

urlpatterns = patterns("",
    url(r"^(?P<package>[^/]+)/$", ToggleFavorite.as_view(), name="toggle_favorite"),
)
