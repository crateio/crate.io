import json

from django.http import HttpResponse
from django.views.generic.base import View

from favorites.models import Favorite
from packages.models import Package


class ToggleFavorite(View):

    def render_json(self, **data):
        return HttpResponse(json.dumps(data), mimetype="application/json")

    def post(self, request, *args, **kwargs):
        try:
            package = Package.objects.get(name=kwargs.get("package"))
        except Package.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), success=False, message="Package does not exist")

        fav = Favorite.objects.filter(package=package, user=request.user)

        if fav:
            fav.delete()
            return self.render_json(package=package.name, success=True, action="unfavorite")
        else:
            Favorite.objects.create(package=package, user=request.user)
            return self.render_json(package=package.name, success=True, action="favorite")
