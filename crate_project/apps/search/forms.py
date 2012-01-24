from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from haystack.inputs import AutoQuery
from haystack.query import SQ


class SearchForm(HaystackSearchForm):
    has_releases = forms.BooleanField(required=False, initial=True)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

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

        if self.cleaned_data.get('has_releases'):
            sqs = sqs.filter(release_count__gt=0)

        if self.cleaned_data['start_date']:
            sqs = sqs.filter(modified__gte=self.cleaned_data['start_date'])

        if self.cleaned_data['end_date']:
            sqs = sqs.filter(modified__lte=self.cleaned_data['end_date'])

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
