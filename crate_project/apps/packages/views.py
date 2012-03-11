from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView

from packages.models import Release


class ReleaseDetail(DetailView):

    model = Release
    queryset = Release.objects.all().prefetch_related(
                                        "uris",
                                        "files",
                                        "requires",
                                        "provides",
                                        "obsoletes",
                                        "classifiers",
                                    )

    def get_context_data(self, **kwargs):
        ctx = super(ReleaseDetail, self).get_context_data(**kwargs)
        ctx.update({
            "release_files": self.object.files.filter(hidden=False),
            "version_specific": self.kwargs.get("version", None),
        })
        return ctx

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        package = self.kwargs["package"]
        version = self.kwargs.get("version", None)

        queryset = queryset.filter(package__name=package)

        if version:
            queryset = queryset.filter(version=version)
        else:
            queryset = queryset.filter(hidden=False).order_by("-order")[:1]

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
