from django import forms
from decimal import Decimal

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

    algorithm = forms.ChoiceField(
        choices=(("1","PretSa"),("2","Other"),)
    )
    
    t = forms.DecimalField(
        label='Select t'
        )

    k = forms.IntegerField(
        label='Select k'
        )
    
    email = forms.EmailField(
        label='Email adress'
        )
