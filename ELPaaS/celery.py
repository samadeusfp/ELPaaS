from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ELPaaS.settings')

app = Celery('ELPaaS', broker='pyamqp://guest@localhost//')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

#all ten minutes, cleanup old files
app.conf.beat_schedule = {
    "remove-overdue-files": {
        "task": "eventlogUploader.tasks.remove_overdue_files",
        "schedule": 10.0
    }
}

@app.task
def see_you():
    print("See you in ten seconds!")
