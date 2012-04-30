import json

from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required

from lists.models import List
from packages.models import Package


class RemoveFromList(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RemoveFromList, self).dispatch(*args, **kwargs)

    def render_json(self, **data):
        return HttpResponse(json.dumps(data), mimetype="application/json")

    def post(self, request, *args, **kwargs):
        try:
            package = Package.objects.get(name=kwargs.get("package"))
            user_list = List.objects.get(name=kwargs.get("list"), user=request.user)
        except Package.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=False, message=_("Package does not exist"))
        except List.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=False, message=_("List does not exist"))

        user_list.packages.remove(package)

        return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=True, message=_("Successfully removed %(package)s from %(list)s.") % kwargs)
