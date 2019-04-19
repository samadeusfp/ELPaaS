from django.shortcuts import render

from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from eventlogUploader.models import Document
from eventlogUploader.forms import DocumentForm
from django.contrib import messages 
import os

#initial rendering of index page, renders upload form and uploaded files
def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            algorithm = form.cleaned_data['algorithm']
            
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

        #TODO let this run as a background task
            command = "python algorithms/PRETSA/runPretsa.py " + path + " " + str(kValue) + " " + str(tValue) + " "+ pathDB + " &"
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
