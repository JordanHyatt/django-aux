import django_tables2 as tables
from django_tables2 import A
from main.models import *
from django_aux.columns import CollapseColumn, RoundNumberColumn, BarChartColumn

class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    adjectives = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives') # regular iterable
    adjectives_links = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives W/links', hyperlink=True) # Iterable with links
    adjectives_dyn_labels = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives W/Dyn Labels', label_accessor='last_name') # iterable with dynamic labels
    pdict = CollapseColumn(accessor='attr_dict', dictionary=True, label_accessor='last_name') # dict 
    longtxt = CollapseColumn(accessor='long_text', style='background-color: blue; color: yellow') # non-iterable using style
    org = CollapseColumn(accessor='org', label_accessor='org__name') # non-iterable with dynamic label
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True) # RoundNumberColumn
    delete = tables.LinkColumn('person-delete', verbose_name='', text='[Delete]', args=[A('id')])
    class Meta:
        model = Person
        exclude = ['uuid']
        sequence = []


