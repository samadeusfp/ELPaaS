from django.shortcuts import render,redirect
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import BadHeaderError, send_mail
from django.urls import reverse
from django.conf import settings
from eventlogUploader.models import Document
from eventlogUploader.forms import DocumentForm, DownloadForm, ColumnSelectForm
from django.contrib import messages
import os
import hashlib
from django.utils import timezone
import pytz
import datetime
import subprocess
import time



from .tasks import handle_pretsa_upload, handle_laplace_df_upload, handle_laplace_tv_upload,handle_pripel_upload, handle_risk_upload, handle_risk_upload_with_columns

def handle_view_file(request):
    if request.method == 'GET':
        token = request.GET['token']
        document=list(Document.objects.filter(token = token).values())
        if document:
            document_name=document[0]['docfile']
            document_name=document_name.replace(token,"")[1:]
            #print(document[0]['algorithm'])
        upload_form = DocumentForm(initial = {'algorithm':'1'})
        download_form = DownloadForm()
        columns = tuple()
        if document[0]['algorithm']=='Quantifying Re-identification Risk':
            columns = tuple(token_to_column_list(token))
        column_form = ColumnSelectForm(case_attr_var= columns,event_attr_var= columns,token_var=token)

        #Load documents for the list page
        if not document:
            return render(request,'index.html',{'not_found': True,
                                                'upload_form': upload_form,
                                                'download_form': download_form,
                                                'column_form': column_form}
                          )
        else:
            return render(request,'index.html',{'document':document,
                                                'document_name':document_name,
                                                'token': token,
                                                'upload_form': upload_form,
                                                'download_form': download_form,
                                                'column_form': column_form}
                          )
    return redirect('index')
    
def setValues(request):
    case_attributes = {}
    case_attributes = request.POST.getlist('case_attr')
    print(case_attributes)
    event_attributes = {}
    event_attributes = request.POST.getlist('event_attr')
    print(event_attributes)
    
    return case_attributes,event_attributes
    
def convert_list_to_string(org_list, seperator=','):
    
    return seperator.join(org_list)
    
def handle_column_select(request):
    if request.method == 'POST':
        
        projection = request.POST['projection']
        token = request.POST['token']
        case_attributes,event_attributes = setValues(request)
        
        column_form = ColumnSelectForm(case_attributes,event_attributes,projection,token,initial={'projection': '1'})

            
        case_string= convert_list_to_string(case_attributes)
        event_string= convert_list_to_string(event_attributes)
        
        if not case_string:
            case_string ='$empty_string$'
        if not event_string:
            event_string ='$empty_string$'
        
        
        media_path = os.path.join(os.getcwd(), "media", token)
        db_path = os.path.join(os.getcwd(),"db.sqlite3")
        
        handle_risk_upload_with_columns.delay(projection, case_string, event_string, media_path, db_path, token)
        redirect_var = "/view/?token="
        upload_form = DocumentForm(initial = {'algorithm':'1'})
        download_form = DownloadForm()
        
        return redirect(redirect_var+token, permanent=True)
    return redirect('index')

        

def handle_file_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            
            #get values from form
            algorithm = form.cleaned_data['algorithm']
            algorithm_text=""
            if algorithm == '1':
                algorithm_text="PRETSA"
            elif algorithm == '2':
                algorithm_text="Laplace directly-follows based"
            elif algorithm == '3':
                algorithm_text="Laplace trace-variant based"
            elif algorithm == '4':
                algorithm_text="PRIPEL"
            elif algorithm == '5':
                algorithm_text="Quantifying Re-identification Risk"

            #generate token, save to db and to media folder
            upload_time = timezone.now()
            #upload_time = datetime.datetime.now(tzinfo=pytz.UTC)
            expiration_time = upload_time+ datetime.timedelta(+30)
            
            secure_token = generate_token(request.FILES['docfile'], algorithm)
            newdoc = Document(docfile = request.FILES['docfile'],
                              token = secure_token,
                              status = "PROCESSING",
                              algorithm = algorithm_text,
                              uploaded_on = upload_time,
                              expires_on = expiration_time)
            newdoc.save()

            #get all parameter for execution script
            file_name = request.FILES['docfile'].name
            media_path = os.path.join(os.getcwd(), "media",secure_token,file_name)
            db_path = os.path.join(os.getcwd(),"db.sqlite3")
            redirect_var = "/view/?token="  

            #call algorithm script using celery - see functions in tasks.py
            if algorithm =='1':
                kValue = form.cleaned_data['k']
                tValue = form.cleaned_data['t']
                anonValue = form.cleaned_data['anon']
                metadataValue = form.cleaned_data['metadata']
                handle_pretsa_upload.delay(kValue, tValue, anonValue, media_path, db_path, secure_token, metadataValue)   
            elif algorithm =='2':
                epsilonValue = form.cleaned_data['epsilon']
                metadataValue = form.cleaned_data['metadata']
                handle_laplace_df_upload.delay(epsilonValue, media_path, db_path, secure_token, metadataValue)
            elif algorithm =='3':
                epsilonValue = form.cleaned_data['epsilon']
                nValue = form.cleaned_data['n']
                pValue = form.cleaned_data['p']
                metadataValue = form.cleaned_data['metadata']
                handle_laplace_tv_upload.delay(epsilonValue, nValue, pValue, media_path, db_path, secure_token, metadataValue)
            elif algorithm =='4':
                epsilonValue = form.cleaned_data['epsilon']
                nValue = form.cleaned_data['n']
                kValue = form.cleaned_data['pripel_k']
                metadataValue = form.cleaned_data['metadata']
                handle_pripel_upload.delay(epsilonValue, nValue, kValue, media_path, db_path, secure_token, metadataValue)             
            elif algorithm =='5':
                identifier = form.cleaned_data['unique_identifier']
                incList = form.cleaned_data['attributes']
                exList = form.cleaned_data['attributes_to_exclude']
                handle_risk_upload.delay(media_path, db_path, secure_token)
                redirect_var = "/view/?token="
                #columns = token_to_column_list(secure_token)
                #print(columns)
            else:
                redirect_var = "/view/?token="

            #return redirect('/view/?token='+secure_token, permanent=True)
            return redirect(redirect_var+secure_token, permanent=True)
    return redirect('index')

#initial rendering of index page, renders upload form and uploaded files if token has been inputted
#def index(request):
#    upload_form = DocumentForm(initial = {'algorithm':'1'})
#    download_form = DownloadForm()
#    return render(request, 'index.html', {'upload_form': upload_form, 'download_form': download_form})


#initial rendering of index page, renders upload form and uploaded files if token has been inputted
def index(request):
    if request.method == 'GET' and 'token' in request.GET:
        token = request.GET['token']
    else:
        token = None 
    upload_form = DocumentForm(initial = {'algorithm':'1'})
    download_form = DownloadForm()
    column_form = ColumnSelectForm(case_attr_var=tuple(),event_attr_var=tuple(),token_var=token)

    return render(request, 'index.html', {'upload_form': upload_form, 'download_form': download_form, 'column_form': column_form})

def generate_token(docfile, algorithm):
    m = hashlib.sha256()
    m.update(str.encode(algorithm))
    m.update(str.encode(str(datetime.datetime.now(tz=timezone.utc))))
    return m.hexdigest()
    
def token_to_column_list(secure_token):
    if secure_token == None:
        columns = []
    else:
        columns = []
        column_path = os.path.join(os.getcwd(), "media",secure_token,"columns.txt")
        while not os.path.exists(column_path):
            time.sleep(1)
        
        with open(column_path, 'r') as filehandle:
            columns = [current_column.rstrip() for current_column in filehandle.readlines()]
    lista = []  
    for i in columns:
        lista.append((i,i))
    return lista
    

def delete_file(request, token =None):
    instance = Document.objects.get(token=token)
    instance.delete()
    upload_form = DocumentForm(initial = {'algorithm':'1'})
    download_form = DownloadForm()
    column_form = ColumnSelectForm(case_attr_var=tuple(),event_attr_var=tuple(),token_var=token)
    return render(request, 'index.html', {'upload_form': upload_form, 'download_form': download_form, 'column_form': column_form, 'deleted': True})
