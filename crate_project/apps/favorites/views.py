import json

from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from favorites.models import Favorite
from packages.models import Package

FAVORITES_QUERYSET_KEY = "crate:favorites:user(%s):queryset"
FAVORITES_CACHE_VERSION = 2


class ToggleFavorite(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ToggleFavorite, self).dispatch(*args, **kwargs)

    def render_json(self, **data):
        return HttpResponse(json.dumps(data), mimetype="application/json")

    def post(self, request, *args, **kwargs):
        try:
            package = Package.objects.get(name=kwargs.get("package"))
        except Package.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), success=False, message="Package does not exist")

        fav = Favorite.objects.filter(package=package, user=request.user)

        cache.delete(FAVORITES_QUERYSET_KEY % self.request.user.pk, version=FAVORITES_CACHE_VERSION)

        if fav:
            fav.delete()
            return self.render_json(package=package.name, success=True, action="unfavorite")
        else:
            Favorite.objects.create(package=package, user=request.user)
            return self.render_json(package=package.name, success=True, action="favorite")


class UserFavorites(ListView):

    queryset = Favorite.objects.all().select_related("package")
    template_name = "favorites/favorite_list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserFavorites, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        cached = cache.get(FAVORITES_QUERYSET_KEY % self.request.user.pk, version=FAVORITES_CACHE_VERSION)

        if cached:
            return cached

        qs = super(UserFavorites, self).get_queryset()
        qs = qs.filter(user=self.request.user)

        qs = sorted(qs, key=lambda x: x.package.latest.created, reverse=True)

        cache.set(FAVORITES_QUERYSET_KEY % self.request.user.pk, qs, 60 * 60, version=FAVORITES_CACHE_VERSION)

        return qs
