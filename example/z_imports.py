import os, random, time, sys
os.environ['DB_PASSWORD'] = 'postgres'
import time
import django_init
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
from django.conf import settings

# maksure dev apps are on path so linter doesn't freak out
for fn in os.listdir(settings.REPOS_DIR):
    if fn not in settings.ADD_APPS:
        continue
    sys.path.append(os.path.join(settings.REPOS_DIR, fn))


import pandas as pd
DF = pd.DataFrame
from django.conf import settings
from django_pandas.io import read_frame
from tqdm import tqdm
from main.models import *
from django_aux.models import *
from django_aux.utils import *
from django_aux.columns import *
from django_aux_timeperiods.models import *
from django_aux_geo.models import *
from qs_views.models import QsView
from request.models import Request
import calendar
from zoneinfo import ZoneInfo