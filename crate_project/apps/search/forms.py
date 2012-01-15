from haystack.forms import SearchForm as HaystackSearchForm
from haystack.inputs import AutoQuery


class SearchForm(HaystackSearchForm):

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields["q"].widget.attrs.update({
            "class": "offset1 span10"
        })

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        sqs = self.searchqueryset.filter(content=AutoQuery(self.cleaned_data["q"])).filter_or(name=AutoQuery(self.cleaned_data["q"]))

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
