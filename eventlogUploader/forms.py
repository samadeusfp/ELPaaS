from django import forms
from decimal import Decimal
from crispy_forms.helper import FormHelper
from captcha.fields import CaptchaField

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
                 ("3","Laplacian tv-based"),
                 ("4","PRIPEL"),
                 ("5","Quantifying Re-identification Risk")
                ),
        #help_text ="Assumes a .csv File as Input. Returns a .csv File. The File needs to contain the columns 'Case ID', 'Activity' and 'Duration'"
    )

    #pretsa
    t = forms.DecimalField(
        label='Select t',
        help_text='T-closeness: ensures that within each equivalence class there will be a representative distribution of sensitive attributes. The variation allowed compared to the entire data set will be less than value of t. Small values close to 0 allow less variation, value of 1 allows all variation.',
        required = True,
        initial = "0.1",
        min_value=0,
        max_value=1,
        decimal_places =2,
        )

    #pretsa
    k = forms.IntegerField(
        label='Select k',
        help_text='K-anonymity: ensures that there are at least k entries in each equivalence class after data is anonymized. \n Greater value will mean greater but not unbreachable privacy, high values (>50) makes small data sets too generalized to be usable. ',
        required = True,
        initial = "4",
        )
       
    #pretsa
    anon = forms.BooleanField(
        label='Pseudonymize CaseIDs',
        help_text='Requires column "Case ID" - replaces continuous case names with a random unique int.',
        required = False,
        initial = False,
        )


    #laplacian - df and tv,pripel
    epsilon = forms.DecimalField(
        label='Select Epsilon',
        help_text='Adds lapacian noise to either trace variant frequencies (tv) or single events frequencies in directly-follow matrices (df) to satisy epsilon differential privacy.  Smaller epsilon value allows for less variance in uniqueness of entries and therefore more privacy by adding more noise.',
        required = True,
        initial = "0.1",
        )

    #laplacian - tv,pripel
    n = forms.IntegerField(
        label='Select maximum Sequence Length',
        help_text='Maximum length of a subsequence in a trace which will be internally queried. Higher value will take longer to compute and the likelihood grows that new traces not found in the original event log will appear.',
        required = True,
        initial = "6",
        )

    #laplacian - tv
    p = forms.IntegerField(
        label='Select Pruning Parameter',
        help_text='Low-frequency noisy trace-variant counts that occur less often than this value will be ignored. ',
        required = True,
        initial = "30",
        )
        
    #re-identification risk
    unique_identifier = forms.CharField(
        label='Select unique identifier column name',
        required= True,
        initial = "Case ID",
    )
    #re-identification risk
    attributes = forms.CharField(
        label='Attribute names to include in assessment.',
        help_text='Leave blank to include all attribute or choose attributes to exlude. Use ; as delimiter ',
        required= False,
        initial = "",
    )
    #re-identification risk
    attributes_to_exclude = forms.CharField(
        label='Attribute names to exlude in assessment.',
        help_text='Leave blank to include all or those in include field. Use ; as delimiter ',
        required= False,
        initial = "",
    )
    #pripel
    pripel_k = forms.IntegerField(
        label='Select k',
        help_text='Prunning parameter of the trace-variant-query. At least k traces must appear in a noisy variant count to be part of the result of the query. ',
        required = True,
        initial = "4",
    )
    #metadata
    metadata = forms.BooleanField(
        label='Include privacy metadata in .xes output',
        required = False,
        initial = True,
        ) 
    
  

    #email = forms.EmailField(
    #    label='Enter a valid E-mail Adress',
    #    required = True,
    #    )

    captcha = CaptchaField(
        label='Enter the shown symbols'
        )

class DownloadForm(forms.Form):
    token = forms.CharField(
        label='Please enter a secure token',
        required= True
    )

class ColumnSelectForm(forms.Form):
    def __init__(self, case_attr_var=None,event_attr_var=None,projection_var=None, token_var=None, *args, **kwargs):
        super(ColumnSelectForm, self).__init__(*args, **kwargs)
        
        self.fields['projection'] = forms.ChoiceField(
        label='Specify Projection',
        choices=(
                 ("1","activities and timestamps"),
                 ("2","activities, event and case attributes"),
                 ("3","activities and event attributes"),
                 ("4","activities and case attributes"),
                 ("5","activities")
                ),
        )
        self.fields['case_attr'] = forms.MultipleChoiceField(
            label='Specify case attributes',
            help_text='case attributes are consistent for single trace e.g. Age, Day of Birth...',
            required= False,
            widget=forms.SelectMultiple,
            choices=case_attr_var)
        self.fields['event_attr'] = forms.MultipleChoiceField(
            label='Specify event attributes',
            help_text='event attributes are consistent for single event e.g. Timestamp, org:group...',
            required= False,
            widget=forms.SelectMultiple,
            choices=event_attr_var)
            
            
        self.fields['token'] = forms.CharField(
            label='secure token here',
            #widget=forms.HiddenInput(),
            initial=token_var)
            
          
#    def __init__(self, *args, **kwargs):
#        column_var = kwargs.pop('columns', None)
#        super(ColumnSelectForm, self).__init__(*args, **kwargs)
#        if column_var:
#            self.OPTIONS = column_var
    
    
#    colums = open('/media/'
#    OPTIONS = (("1", "CASE ID"),)
#    OPTIONS = kwargs
    
#    def update_choices(self,choices, *args, **kwargs):
    
    
#    Columns = forms.MultipleChoiceField(widget=forms.SelectMultiple,
#                                          choices=OPTIONS)
   