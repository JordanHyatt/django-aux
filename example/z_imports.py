import os, random, time, sys
os.environ['DB_PASSWORD'] = 'postgres'
import time
import django_init
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
from django.conf import settings

# maksure dev apps are on path so linter doesn't freak out
sys.path.append(os.path.join(settings.DAUX_DIR))


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
from request.models import Request
import calendar
from zoneinfo import ZoneInfo