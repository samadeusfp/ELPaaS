from django.shortcuts import render,redirect
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import BadHeaderError, send_mail
from django.urls import reverse
from django.conf import settings
from eventlogUploader.models import Document
from eventlogUploader.forms import DocumentForm, DownloadForm
from django.contrib import messages
import os
import hashlib
import datetime
import subprocess

from .tasks import handle_pretsa_upload, handle_laplace_df_upload, handle_laplace_tv_upload, handle_pripel_upload, handle_risk_upload

def handle_view_file(request):
    if request.method == 'GET':
        token = request.GET['token']
        document=list(Document.objects.filter(token = token).values())
        if document:
            document_name=document[0]['docfile']
            document_name=document_name.replace(token,"")[1:]
        upload_form = DocumentForm(initial = {'algorithm':'1'})
        download_form = DownloadForm()

        #Load documents for the list page
        if not document:
            return render(request,'index.html',{'not_found': True,
                                                'upload_form': upload_form,
                                                'download_form': download_form}
                          )
        else:
            return render(request,'index.html',{'document':document,
                                                'document_name':document_name,
                                                'token': token,
                                                'upload_form': upload_form,
                                                'download_form': download_form}
                          )
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
            upload_time = datetime.datetime.now()
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

            #call algorithm script using celery - see functions in tasks.py
            if algorithm =='1':
                kValue = form.cleaned_data['k']
                tValue = form.cleaned_data['t']
                anonValue = form.cleaned_data['anon']
                handle_pretsa_upload.delay(kValue, tValue, anonValue, media_path, db_path, secure_token)
            elif algorithm =='2':
                epsilonValue = form.cleaned_data['epsilon']
                handle_laplace_df_upload.delay(epsilonValue, media_path, db_path, secure_token)  
            elif algorithm =='3':
                epsilonValue = form.cleaned_data['epsilon']
                nValue = form.cleaned_data['n']
                pValue = form.cleaned_data['p']
                handle_laplace_tv_upload.delay(epsilonValue, nValue, pValue, media_path, db_path, secure_token) 
            elif algorithm =='4':
                epsilonValue = form.cleaned_data['epsilon']
                nValue = form.cleaned_data['n']
                kValue = form.cleaned_data['pripel_k']
                handle_pripel_upload.delay(epsilonValue, nValue, kValue, media_path, db_path, secure_token)  
            elif algorithm =='5':
                identifier = form.cleaned_data['unique_identifier']
                incList = form.cleaned_data['attributes']
                exList = form.cleaned_data['attributes_to_exclude']
                handle_risk_upload.delay( media_path, identifier, incList, exList, db_path, secure_token)

            return redirect('/view/?token='+secure_token, permanent=True)
    return redirect('index')

#initial rendering of index page, renders upload form and uploaded files if token has been inputted
def index(request):
    upload_form = DocumentForm(initial = {'algorithm':'1'})
    download_form = DownloadForm()
    return render(request, 'index.html', {'upload_form': upload_form, 'download_form': download_form})

def generate_token(docfile, algorithm):
    m = hashlib.sha256()
    m.update(str.encode(algorithm))
    m.update(str.encode(str(datetime.datetime.now())))
    return m.hexdigest()

def delete_file(request, token =None):
    instance = Document.objects.get(token=token)
    instance.delete()
    upload_form = DocumentForm(initial = {'algorithm':'1'})
    download_form = DownloadForm()
    return render(request, 'index.html', {'upload_form': upload_form, 'download_form': download_form, 'deleted': True})
