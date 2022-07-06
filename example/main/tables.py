import django_tables2 as tables
from main.models import *
from django_aux.columns import CollapseColumn, RoundNumberColumn, BarChartColumn

class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    adjectives = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives', hyperlink=True)
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True)
    class Meta:
        model = Person
        exclude = []
        sequence = []


