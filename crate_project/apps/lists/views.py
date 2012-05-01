import json

from django.http import HttpResponse
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required

from lists.models import List
from packages.models import Package


class AddToList(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddToList, self).dispatch(*args, **kwargs)

    def render_json(self, **data):
        return HttpResponse(json.dumps(data), mimetype="application/json")

    def get_package(self, package):
        return next(iter(Package.objects.filter(name=package)[:1]), None)

    def get_list(self, list, user):
        return next(iter(List.objects.filter(name=list, user=user)[:1]), None)

    def get_message(self):
        return _("Successfully added %(package)s to %(list)s.") % self.kwargs

    def post(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        package = self.get_package(self.kwargs.get("package"))

        if package is None:
            return self.render_json(
                        package=self.kwargs.get("package"),
                        list=self.kwargs.get("list"),
                        success=False,
                        message=_("Package does not exist")
                    )

        user_list = self.get_list(self.kwargs.get("list", None), user=request.user)

        if user_list is None:
            return self.render_json(
                        package=self.kwargs.get("package"),
                        list=self.kwargs.get("list"),
                        success=False,
                        message=_("List does not exist")
                    )

        user_list.packages.add(package)

        return self.render_json(
                    package=self.kwargs.get("package"),
                    list=self.kwargs.get("list"),
                    success=True,
                    message=self.get_message()
                )


class AddToNewList(AddToList):

    def get_message(self):
        kw = self.kwargs.copy()
        kw.update({
            "list": self.request.POST.get("name"),
            })
        return _("Successfully added %(package)s to %(list)s.") % kw

    def get_list(self, list, user):
        if list is None:
            list = self.request.POST.get("name")

        user_list, c = List.objects.get_or_create(user=user, name=list, defaults={"private": self.request.POST.get("private", True)})

        if not c and user_list.private != self.request.POST.get("private", True):
            user_list.private = self.request.POST.get("private", True)
            user_list.save()

        return user_list


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
