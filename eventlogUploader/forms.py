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
        choices=(("1","PretSa"),
                 ("2","Laplacian df-based"),
                 ("3","Laplacian tv-based")
                )
    )

    #pretsa
    t = forms.DecimalField(
        label='Select t',
        required = True,
        )

    #pretsa
    k = forms.IntegerField(
        label='Select k',
        required = True,
        )


    #laplacian - df and tv
    epsilon = forms.DecimalField(
        label='Select Epsilon',
        required = True,
        )

    #laplacian - tv
    n = forms.IntegerField(
        label='Select n',
        required = True,
        )

    #laplacian - tv
    p = forms.IntegerField(
        label='Select p',
        required = True,
        )

    email = forms.EmailField(
        label='Enter a valid e-mail adress',
        required = True,
        )

class DownloadForm(forms.Form):
    token = forms.CharField(
        label='Please enter a secure token',
        required= True
    )
