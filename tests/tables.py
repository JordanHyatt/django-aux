import django_tables2 as tables
from .models import *


class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    class Meta:
        model = Person
        exclude = []
        sequence = []