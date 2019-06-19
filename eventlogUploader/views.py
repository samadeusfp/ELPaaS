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
            algorithm_text=""
            if algorithm == '1':
                algorithm_text="PretSa"
            if algorithm == '2':
                algorithm_text="Laplace directly-follows based"
            if algorithm == '3':
                algorithm_text="Laplace trace-variant based"
            email = form.cleaned_data['email']         

            #generate token, save to db and to media folder
            #TODO seems to replace space characters with "_" but saves in db without
            upload_time = datetime.datetime.now()
            expiration_time = upload_time+ datetime.timedelta(+30)
            
            secure_token = generate_token(request.FILES['docfile'], email, algorithm)
            newdoc = Document(docfile = request.FILES['docfile'],
                              token = secure_token,
                              status = "PROCESSING",
                              algorithm = algorithm_text,
                              uploaded_on = upload_time,
                              expires_on = expiration_time)
            newdoc.save()

            #TODO /documents as django variable
            #get all parameter for execution script
            file_name = request.FILES['docfile'].name
            media_path = os.getcwd() + "/media/documents/" + file_name
            db_path = os.getcwd() + "/db.sqlite3"

            #send mail with token
            #send_mail_to_user(secure_token, email)


            #Pretsa
            if algorithm =='1':
                kValue = form.cleaned_data['k']
                tValue = form.cleaned_data['t']
                handle_pretsa_upload(kValue, tValue, media_path, db_path, secure_token)
            #laplacian
            if algorithm =='2':
                epsilonValue = form.cleaned_data['epsilon']
                handle_laplace_df_upload(epsilonValue, media_path, db_path, secure_token)  
            if algorithm =='3':
                epsilonValue = form.cleaned_data['epsilon']
                nValue = form.cleaned_data['n']
                pValue = form.cleaned_data['p']
                handle_laplace_tv_upload(epsilonValue, nValue, pValue, media_path, db_path, secure_token)  

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('index'))



#initial rendering of index page, renders upload form and uploaded files if token has been inputted
def index(request):
    upload_form = DocumentForm(initial={
                                        "t":"0.2",
                                        "k":"4",
                                        "epsilon":"0.1",
                                        "n":"10",
                                        "p":"30"})
    download_form = DownloadForm()

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents
    return render(request, 'index.html', {'documents': documents, 'upload_form': upload_form, 'download_form': download_form})


#todo have config file that reads installed methods from folders and links correctly
def handle_pretsa_upload(kValue, tValue, path, pathDB, secure_token):
    command = subprocess.Popen(["python", os.getcwd()+"/algorithms/PRETSA/runPretsa.py", str(path), str(kValue), str(tValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/PRETSA")
    return


def handle_laplace_df_upload(epsilonValue, path, pathDB, secure_token):
    command = subprocess.Popen(["python", os.getcwd()+"/algorithms/Laplacian_df/runLaplacian_df.py", str(path), str(epsilonValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/Laplacian_df")
    return


def handle_laplace_tv_upload(epsilonValue, nValue, pValue, path, pathDB, secure_token):
    command = subprocess.Popen(["python", os.getcwd()+"/algorithms/Laplacian_tv/runLaplacian_tv.py", str(path), str(epsilonValue), str(nValue), str(pValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/Laplacian_tv")
    return


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
    send_mail(subject, message, from_email, [email])
    return
