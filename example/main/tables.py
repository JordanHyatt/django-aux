import django_tables2 as tables
from main.models import *
from django_aux.columns import CollapseColumn, RoundNumberColumn

class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    #dows = CollapseColumn(accessor='dows.all', iterable=True, verbose_name='Days of The Week')
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True)
    class Meta:
        model = Person
        exclude = []
        sequence = []


