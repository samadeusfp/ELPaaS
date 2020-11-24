import string
import os

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from celery import shared_task, task
from subprocess import Popen
from eventlogUploader.models import Document
import shutil

@shared_task
def handle_pretsa_upload(kValue, tValue, anonValue, path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/PRETSA/runPretsa.py", str(path), str(kValue), str(tValue), str(anonValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/PRETSA")
    return

@shared_task
def handle_laplace_df_upload(epsilonValue, path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/laplace_df/privatize_df.py", str(path), str(epsilonValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/laplace_df")
    return

@shared_task
def handle_laplace_tv_upload(epsilonValue, nValue, pValue, path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/laplace_tv/trace_variant_query.py", str(path), str(epsilonValue), str(nValue), str(pValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/laplace_tv")
    return

@shared_task    
def handle_pripel_upload(epsilonValue, nValue, kValue, path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/pripel/pripel.py", str(path), str(epsilonValue), str(nValue), str(kValue), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/pripel")
    return
      
@shared_task
def handle_risk_upload(path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/re_ident_risk/columns.py", str(path), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/re_ident_risk")
    return
    
@shared_task
def handle_risk_upload_with_columns(projection, case_attributes, event_attributes, path, pathDB, secure_token):
    command = Popen(["python", os.getcwd()+"/algorithms/re_ident_risk/re_ident_test.py", str(path), str(projection), str(case_attributes), str(event_attributes), str(pathDB), str(secure_token)], cwd=os.getcwd()+"/algorithms/re_ident_risk")
    return


@shared_task
def remove_overdue_files():
    print("Removing overdue files and database entries")
    #remove overdue database entries
    Document.objects.filter(expires_on__lte = datetime.now()).delete()
    
    #remove all directories that do not have a database entry that is overdue
    directories = os.listdir(settings.MEDIA_ROOT)
    for directory in directories:
        if not Document.objects.filter(token = directory).exists():
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, directory))
