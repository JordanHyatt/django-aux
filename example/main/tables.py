import django_tables2 as tables
from django_tables2 import A
from main.models import *
from django_aux.columns import CollapseColumn, RoundNumberColumn, BarChartColumn

class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    adjectives = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives', hyperlink=True)
    persondict = CollapseColumn(accessor='attr_dict', dictionary=True, label_accessor='last_name')
    longtxt = CollapseColumn(accessor='long_text', style='background-color: blue; color: yellow')
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True)
    delete = tables.LinkColumn('person-delete', verbose_name='', text='[Delete]', args=[A('id')])
    class Meta:
        model = Person
        exclude = []
        sequence = []


