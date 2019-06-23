Required packages:
Python:
sqlite3
pandas
scipy
numpy
anytree
hashlib
datetime
subprocess
requests
time
pm4py
django
django-crispy-forms
django-env-overrides
django-simple-captcha

R:
bupaR
readR
dplyr
tidyr
tidyverse
stringr
xesreadR
DiagrammeRsvg

What to do, before server can be run the first time:
-Download the required packages
-Delete all migrations and the database:
"find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm db.sqlite3"
-Run "python manage.py makemigrations"
-Run "python manage.py migrate"
-Enable the Sending of e-Mails:
	In ElPaas/settings.py scroll down to the bottom and exchange the data in the
	following fields with the smtp settings of your desired mail hoster that
	should be used:
		EMAIL_HOST
		EMAIL_PORT
		EMAIL_Host_USER
		EMAIL_HOST_PASSWORD



How to run the server:
-"python manage.py runserver"
