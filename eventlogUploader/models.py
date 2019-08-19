from django.db import models
import os

def upload_path_generation(instance, filename):
    return os.path.join('documents/%s/'%instance.token, filename)
    return 'documents/'
# Create your models here.

class Document(models.Model):
    token = models.CharField(max_length=100)
    docfile = models.FileField(upload_to=upload_path_generation)
    status = models.CharField(max_length=30)
    algorithm = models.CharField(max_length=100)
    uploaded_on = models.DateTimeField()
    expires_on = models.DateTimeField()


