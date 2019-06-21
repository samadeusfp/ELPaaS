from django import forms
from decimal import Decimal
from crispy_forms.helper import FormHelper

class DocumentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)

        #change help texts to popover
        #for field in self.fields:
        #    help_text = self.fields[field].help_text
        #    self.fields[field].help_text = None
        #    if help_text != '':
        #        self.fields[field].widget.attrs.update({'class':'has-popover', 'data-toggle':'popover' , 'data-trigger':'focus', 'data-content':help_text, 'data-placement':'right', 'data-container':'body'})
         
    docfile = forms.FileField(
        label='Select a .xes-file',
        required = True,
    )

    algorithm = forms.ChoiceField(
        choices=(
                 ("1","PRETSA"),
                 ("2","Laplacian df-based"),
                 ("3","Laplacian tv-based")
                ),
        #help_text ="Assumes a .csv File as Input. Returns a .csv File. The File needs to contain the columns 'Case ID', 'Activity' and 'Duration'"
    )

    #pretsa
    t = forms.DecimalField(
        label='Select t',
        required = True,
        initial = "0.1",
        )

    #pretsa
    k = forms.IntegerField(
        label='Select k',
        required = True,
        initial = "4",
        )


    #laplacian - df and tv
    epsilon = forms.DecimalField(
        label='Select Epsilon',
        required = True,
        initial = "0.1",
        )

    #laplacian - tv
    n = forms.IntegerField(
        label='Select maximum Sequence Length',
        required = True,
        initial = "10",
        )

    #laplacian - tv
    p = forms.IntegerField(
        label='Select Pruning Pramater',
        required = True,
        initial = "30",
        )

    email = forms.EmailField(
        label='Enter a valid E-mail Adress',
        required = True,
        )

class DownloadForm(forms.Form):
    token = forms.CharField(
        label='Please enter a secure token',
        required= True
    )
