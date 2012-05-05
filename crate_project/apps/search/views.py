import urllib
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.translation import ugettext as _

from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import FormMixin

from saved_searches.models import SavedSearch
from search.forms import SearchForm


class Search(TemplateResponseMixin, FormMixin, View):

    searchqueryset = None
    load_all = False
    paginate_by = None
    allow_empty = True
    form_class = SearchForm
    paginator_class = Paginator
    search_key = 'general_search'

    def get_template_names(self):
        if "q" in self.request.GET:
            return ["search/results.html"]
        return ["homepage.html"]

    def get_searchqueryset(self):
        return self.searchqueryset

    def get_load_all(self):
        return self.load_all

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_paginate_by(self):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        if self.paginate_by is None:
            return getattr(settings, "HAYSTACK_SEARCH_RESULTS_PER_PAGE", 20)
        return self.paginate_by

    def get_paginator(self, results, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(results, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)

    def paginate_results(self, results, page_size):
        """
        Paginate the results, if needed.
        """
        paginator = self.get_paginator(results, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get("page") or self.request.GET.get("page") or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(_(u"Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404(_(u"Invalid page (%(page_number)s)") % {
                                "page_number": page_number
            })

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {
            "initial": self.get_initial(),
            "searchqueryset": self.get_searchqueryset(),
            "load_all": self.get_load_all(),
        }
        if "q" in self.request.GET:
            kwargs.update({
                "data": self.request.GET,
            })
        return kwargs

    def form_valid(self, form):
        query = form.cleaned_data["q"]
        results = form.search()
        narrow = []

        faceted_by = {
            "python": None,
            "os": None,
            "license": None,
            "implementation": None,
        }

        # Check for facets.
        if self.request.GET.get("python"):
            faceted_by["python"] = self.request.GET["python"]
            narrow.append("python_versions:%s" % self.request.GET["python"])

        if self.request.GET.get("os"):
            faceted_by["os"] = self.request.GET["os"]
            narrow.append("operating_systems:%s" % self.request.GET["os"])

        if self.request.GET.get("license"):
            faceted_by["license"] = self.request.GET["license"]
            narrow.append("licenses:%s" % self.request.GET.get("license"))

        if self.request.GET.get("implementation"):
            faceted_by["implementation"] = self.request.GET["implementation"]
            narrow.append("implementations:%s" % self.request.GET.get("implementation"))

        if len(narrow):
            results = results.narrow(" AND ".join(narrow))

        page_size = self.get_paginate_by()

        if page_size:
            facets = results.facet("python_versions").facet("operating_systems").facet("licenses").facet("implementations").facet_counts()
            paginator, page, results, is_paginated = self.paginate_results(results, page_size)

            # Save it!
            self.save_search(page, query, results)

            # Grumble.
            duped = self.request.GET.copy()
            try:
                del duped["page"]
            except KeyError:
                pass
            query_params = urllib.urlencode(duped, doseq=True)
        else:
            facets = {}
            query_params = ""
            paginator, page, is_paginated = None, None, False

        print faceted_by

        ctx = {
            "form": form,
            "query": query,
            "results": results,
            "page": page,
            "paginator": paginator,
            "is_paginated": is_paginated,
            "facets": facets,
            "faceted_by": faceted_by,
            "query_params": query_params,
        }

        return self.render_to_response(self.get_context_data(**ctx))

    # Copy-pasta from saved_searches with light modification...
    def save_search(self, page, query, results):
        """
        Only save the search if we're on the first page.
        This will prevent an excessive number of duplicates for what is
        essentially the same search.
        """
        if query and page.number == 1:
            # Save the search.
            saved_search = SavedSearch(
                search_key=self.search_key,
                user_query=query,
                result_count=len(results)
            )

            if hasattr(results, 'query'):
                query_seen = results.query.build_query()

                if isinstance(query_seen, basestring):
                    saved_search.full_query = query_seen

            if self.request.user.is_authenticated():
                saved_search.user = self.request.user

            saved_search.save()

    def get(self, request, *args, **kwargs):
        self.request = request

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if "q" in self.request.GET:
            if form.is_valid():
                return self.form_valid(form)
            else:
                self.form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
