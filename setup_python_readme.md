# Installation Python

## Required packages

### Python

* sqlite3-*
* pandas
* scipy
* numpy
* anytree
* hashlib-*
* datetime
* subprocess-*
* requests
* time-*
* pm4py 1.3
* django
* django-crispy-forms
* django-env-overrides
* django-simple-captcha
* django-cleanup !
* eventlet !
* celery
* django-celery-beat
* p-privacy-metadata

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

## Start
How to run the server:
* First start Celery and Celery Beat by running
```
celery -A ELPaaS worker -B -l info -P eventlet
```
* Then, in a different shell start the server by running
```
python manage.py runserver
```

* Note, that on Windows machines you need to start Celery and Celery Beat seperately, by starting Celery
```
celery -A ELPaaS worker -l info -P eventlet
```
* And then starting Celery Beat in a different terminal
```
$ celery -A ELPaaS beat
```
