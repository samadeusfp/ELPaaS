from django.db import models
from django.conf import settings
import os
import shutil

def upload_path_generation(instance, filename):
    return os.path.join('%s/'%instance.token, filename)

    
class Document(models.Model):
    token = models.CharField(max_length=100)
    docfile = models.FileField(upload_to=upload_path_generation)
    status = models.CharField(max_length=30)
    algorithm = models.CharField(max_length=100)
    uploaded_on = models.DateTimeField()
    expires_on = models.DateTimeField()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs) #delete save entry
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, self.token))
        