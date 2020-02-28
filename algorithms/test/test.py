import sys

import pandas as pd
import numpy as np

celery -A ELPaaS worker -l info -P eventlet
python manage.py runserver

http://127.0.0.1:8000/