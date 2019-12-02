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

## Start
How to run the server:
* First start Celery and Celery Beat by running in the command line
```
celery -A ELPaaS worker -B -l info -P eventlet
```
* Then, in a different shell start then server by running
```
python manage.py runserver
```
