from django.db import models


# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/')
    token = models.CharField(max_length=100)
    status = models.CharField(max_length=30)
