import json

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.contrib import messages
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

        messages.success(request, self.get_message())

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

        defaults = {
            "private": self.request.POST.get("private", False),
            "description": self.request.POST.get("description", ""),
        }
        user_list, c = List.objects.get_or_create(user=user, name=list, defaults=defaults)

        if not c and user_list.private != self.request.POST.get("private", False):
            user_list.private = self.request.POST.get("private", False)
            user_list.save()

        if not c and user_list.description != self.request.POST.get("description", ""):
            user_list.description = self.request.POST.get("description", "")
            user_list.save()

        return user_list


class RemoveFromList(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RemoveFromList, self).dispatch(*args, **kwargs)

    def render_json(self, **data):
        return HttpResponse(json.dumps(data), mimetype="application/json")

    def get_message(self):
        return _("Successfully removed %(package)s from %(list)s.") % self.kwargs

    def post(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        try:
            package = Package.objects.get(name=kwargs.get("package"))
            user_list = List.objects.get(name=kwargs.get("list"), user=request.user)
        except Package.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=False, message=_("Package does not exist"))
        except List.DoesNotExist:
            return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=False, message=_("List does not exist"))

        user_list.packages.remove(package)

        messages.success(request, self.get_message())

        return self.render_json(package=kwargs.get("package"), list=kwargs.get("list"), success=True, message=self.get_message())


class ListsList(ListView):

    queryset = List.objects.all().order_by("name")

    def get_queryset(self):
        qs = super(ListsList, self).get_queryset()
        qs = qs.filter(user__username=self.kwargs.get("username"))

        if self.request.user.is_authenticated():
            qs = qs.filter(Q(private=False) | Q(private=True, user=self.request.user))
        else:
            qs = qs.filter(private=False)

        return qs


class ListDetail(DetailView):

    queryset = List.objects.all().select_related("packages")

    def get_queryset(self):
        qs = super(ListDetail, self).get_queryset()
        qs = qs.filter(user__username=self.kwargs.get("username"))

        if self.request.user.is_authenticated():
            qs = qs.filter(Q(private=False) | Q(private=True, user=self.request.user))
        else:
            qs = qs.filter(private=False)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(ListDetail, self).get_context_data(**kwargs)

        ctx.update({
            "packages": sorted(self.object.packages.all(), key=lambda x: x.latest.created, reverse=True)
        })

        return ctx
