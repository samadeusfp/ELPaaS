from django.shortcuts import render

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from eventlogUploader.models import Document
from eventlogUploader.forms import DocumentForm
import os


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()
            file = request.FILES['docfile']
            path = os.getcwd() + "/media/documents/" + file.name
            kValue = 4
            tValue = 0.2
            pathDB = os.getcwd() + "/db.sqlite3"
            command = "python algorithms/PRETSA/runPretsa.py " + path + " " + str(kValue) + " " + str(tValue) + " "+ pathDB + " &"
            os.system(command)

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()


    # Render list page with the documents and the form
    return render(request, 'list.html', {'documents': documents, 'form': form})