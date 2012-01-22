from django import forms


class WaitingListForm(forms.Form):
    email = forms.EmailField(max_length=75, widget=forms.TextInput(attrs={"placeholder": "Email", "class": "span5"}))
