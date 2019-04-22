from django.shortcuts import render

from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import BadHeaderError, send_mail
from django.urls import reverse
from django.conf import settings

from eventlogUploader.models import Document
from eventlogUploader.forms import DocumentForm
from django.contrib import messages 
import os
import hashlib
import datetime

#initial rendering of index page, renders upload form and uploaded files
def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            algorithm = form.cleaned_data['algorithm']
            email = form.cleaned_data['email']
        #TODO clarrify if these should be default values?
            #kValue = 4
            #tValue = 0.2
            kValue = form.cleaned_data['k']
            tValue = form.cleaned_data['t']

        #TODO clarify why file is explicitly saved           
            #newdoc = Document(docfile = request.FILES['docfile'])
            #newdoc.save()
            
            file = request.FILES['docfile']
            path = os.getcwd() + "/media/documents/" + file.name
            pathDB = os.getcwd() + "/db.sqlite3"

            #send mail with token
            secure_token = generate_token(request.FILES['docfile'], email, algorithm)
            send_mail =(secure_token, email)

            #save into db with token

        #TODO let this run as a background task
            command = "python algorithms/PRETSA/runPretsa.py " + path + " " + str(kValue) + " " + str(tValue) + " " + pathDB + " " + secure_token + " &"
            os.system(command)

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('index'))
    else:
        form = DocumentForm(
                initial={"t":"0.2", "k":"4"}
                )
                # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(request, 'index.html', {'documents': documents, 'form': form})

def generate_token(docfile, email, algorithm):
    m = hashlib.sha256()
    m.update(str.encode(email))
    m.update(str.encode(algorithm))
    m.update(str.encode(str(datetime.datetime.now())))
    return m.hexdigest()

#TODO proper settings for mail management
def send_mail(secure_token, email):
        subject = 'ELPaaS - your secure download token'
        message = 'Hello,'
        'In this mail you can find your secure token that has been generated the'
        'log file that you have uploaded to ELPaaS for Privatization.\n'
        'Use this token to view the status of your file or download it from WEBPAGE.\n'
        '\n'
        'Best regards,\n'
        'your ELPaaS team\n'
        '\n'
        'Warning. This in an autmated mail. Please do not reply to this mail.'
        from_email = 'noreply@elpaas.com'
        
        if subject and message and from_email:
            try:
                send_mail(subject, message, from_email, [email])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        return
