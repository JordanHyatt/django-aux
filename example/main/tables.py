import django_tables2 as tables
from main.models import *


class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    #dows = CollapseColumn(accessor='dows.all', iterable=True, verbose_name='Days of The Week')
    class Meta:
        model = Person
        exclude = []
        sequence = []


