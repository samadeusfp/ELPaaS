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

How to run the server:
-"python manage.py runserver"
