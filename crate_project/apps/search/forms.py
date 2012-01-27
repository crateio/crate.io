from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from haystack.inputs import AutoQuery
from haystack.query import SQ


class SearchForm(HaystackSearchForm):
    has_releases = forms.BooleanField(label="Has Releases", required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields["q"].widget.attrs.update({
            "class": "span10",
            "placeholder": "Search",
        })

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        sqs = self.searchqueryset.filter(SQ(content=AutoQuery(self.cleaned_data["q"])) | SQ(name=AutoQuery(self.cleaned_data["q"])))

        if self.cleaned_data.get("has_releases"):
            sqs = sqs.filter(release_count__gt=0)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
