from django import forms
from .models import Item, Lend

class LendForm(forms.ModelForm):
    class Meta:
        model = Lend
        fields = ('responsible', 'lend_start', 'lend_end', 'notes', 'amount', 'item')