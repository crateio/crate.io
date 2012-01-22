from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from privatebeta.forms import WaitingListForm
from privatebeta.models import WaitingList


class PrivateBetaMiddleware(object):

    def process_request(self, request):
        ALLOWED_URLS = getattr(settings, "PRIVATE_BETA_ALLOWED_URLS", [])

        if request.user.is_authenticated() or request.path in ALLOWED_URLS:
            return

        if request.method == "POST":
            form = WaitingListForm(request.POST)
            if form.is_valid():
                WaitingList.objects.get_or_create(email=form.cleaned_data["email"])
                request.session["submitted_form"] = True
                return HttpResponseRedirect(request.build_absolute_uri())
        else:
            form = WaitingListForm()

        submitted = request.session.get("submitted_form", False)

        if submitted:
            del request.session["submitted_form"]

        return render(request, "privatebeta/index.html", {"form": form, "submitted": submitted})
