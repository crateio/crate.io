from django import forms

from lists.models import List

class CreateListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "private"]
