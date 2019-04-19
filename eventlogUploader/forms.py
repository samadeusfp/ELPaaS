from django import forms
from decimal import Decimal
from crispy_forms.helper import FormHelper

class DocumentForm(forms.Form):
        
    docfile = forms.FileField(
        label='Select a file',
        required = True,
        #widget=forms.FileInput(
        #        attrs={'class':'btn btn-primary'}
        #)
        
    )

    algorithm = forms.ChoiceField(
        choices=(("1","PretSa"),("2","Other"),)
    )
    
    t = forms.DecimalField(
        label='Select t',
        required = True,
        )

    k = forms.IntegerField(
        label='Select k',
                required = True
        )
    
    email = forms.EmailField(
        label='Email adress',
                required = True
        )
