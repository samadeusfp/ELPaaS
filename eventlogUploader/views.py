from django.shortcuts import render

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


def handle_view_file(request):
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            input_token = form.cleaned_data['token']
            documents=list(Document.objects.filter(token = input_token).values())
            return JsonResponse(documents, safe= False)


def handle_file_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            #get values from form
            algorithm = form.cleaned_data['algorithm']
            email = form.cleaned_data['email']
            kValue = form.cleaned_data['k']
            tValue = form.cleaned_data['t']

            #generate token, save to db and to media folder
            secure_token = generate_token(request.FILES['docfile'], email, algorithm)
            newdoc = Document(docfile = request.FILES['docfile'], token = secure_token, status="PROCESSING" )
            newdoc.save()

            #TODO /documents as django variable
            #get all parameter for execution script
            file_name = request.FILES['docfile'].name
            path = os.getcwd() + "/media/documents/" + file_name
            pathDB = os.getcwd() + "/db.sqlite3"

            #send mail with token
            send_mail_to_user(secure_token, email)

            #TODO execute chosen algorithm
            command = subprocess.Popen(["python", os.getcwd()+"/algorithms/PRETSA/runPretsa.py", str(path), str(kValue), str(tValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/PRETSA")
            #command = 'python algorithms/PRETSA/runPretsa.py "' + path + '" ' + str(kValue) + ' ' + str(tValue) + ' ' + pathDB + ' ' + secure_token + ' &'
            #os.system(command)

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('index'))



#initial rendering of index page, renders upload form and uploaded files if token has been inputted
def index(request):
    #TODO clarify if these should be default values?
    upload_form = DocumentForm(initial={"t":"0.2", "k":"4"})
    download_form = DownloadForm()

    # Load documents for the list page
    #TODO seems unneccessary
    documents = Document.objects.all()

    # Render list page with the documents
    return render(request, 'index.html', {'documents': documents, 'upload_form': upload_form, 'download_form': download_form})



def generate_token(docfile, email, algorithm):
    m = hashlib.sha256()
    m.update(str.encode(email))
    m.update(str.encode(algorithm))
    m.update(str.encode(str(datetime.datetime.now())))
    return m.hexdigest()



#TODO proper settings for mail management
def send_mail_to_user(secure_token, email):
    subject = 'ELPaaS - your secure download token'
    message ="""Hello,
In this mail you can find your secure token that has been generated for the log file that you have uploaded to ELPaaS.
Use this token to view the status of your file or download it from WEBPAGE
\n
Your personal Token is:
{secure_token}
\n
Best regards,
your ELPaaS team
\n
Note: This in an autmated mail. Please do not reply to this mail.""".format(secure_token=str(secure_token))
    from_email = settings.EMAIL_HOST_USER
    #try:
    send_mail(subject, message, from_email, [email])
    #except BadHeaderError:
    #    return HttpResponse('Invalid header found.')
    return
