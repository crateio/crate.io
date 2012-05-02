from django import forms

from lists.models import List


class CreateListForm(forms.ModelForm):

    class Meta:
        model = List
        fields = ["name", "description", "private"]

    def __init__(self, *args, **kwargs):
        super(CreateListForm, self).__init__(*args, **kwargs)

        self.fields["description"].widget = forms.Textarea()
