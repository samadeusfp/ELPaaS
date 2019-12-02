# Installation Python

## Required packages

### Python

* sqlite3
* pandas
* scipy
* numpy
* anytree
* hashlib
* datetime
* subprocess
* requests
* time
* pm4py
* django
* django-crispy-forms
* django-env-overrides
* django-simple-captcha
* celery
* django-celery-beat

### R

* bupaR
* readR
* dplyr
* tidyr
* tidyverse
* stringr
* xesreadR
* DiagrammeRsvg

### Misc
* [RabbitMQ for Celery](https://www.rabbitmq.com/)

## Preparation

What to do, before server can be run the first time:

* Download the required packages
* Delete all migrations and the database:
```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm db.sqlite3
```

* Run
```
python manage.py makemigrations
```
* Run
```
python manage.py migrate
```
* Enable the Sending of e-Mails:
	In ElPaas/settings.py scroll down to the bottom and exchange the data in the
	following fields with the smtp settings of your desired mail hoster that
	should be used:
	* EMAIL_HOST
	* EMAIL_PORT
	* EMAIL_HOST_USER		
	* EMAIL_HOST_PASSWORD
	* EMAIL_SENDER


## Start
How to run the server:
* Run
```
celery -A ELPaaS worker -B -l info -P eventlet
```
* This will start Celery and all cron jobs in the background.
* Then, in a different shell run
```
python manage.py runserver
```
