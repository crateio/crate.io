from django.conf.urls import patterns, url

from favorites.views import ToggleFavorite, UserFavorites

urlpatterns = patterns("",
    url(r"^$", UserFavorites.as_view(), name="user_favorites"),
    url(r"^(?P<package>[^/]+)/$", ToggleFavorite.as_view(), name="toggle_favorite"),
)
