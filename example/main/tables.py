import django_tables2 as tables
from django.db.models import F, Q
from django_tables2 import A
from main.models import *
from django_aux.columns import CollapseColumn, RoundNumberColumn, CollapseDataFrameColumn


hist_values_args = [
    'first_name', 'last_name', 'salary',
    'history_date', 'history_change_reason', 'history_type', 'history_relation_id', 'history_user_last_name',
]
hist_values_kwargs = dict(
    history_username = F('history_user__username')
)
hist_annotate_kwargs = dict(history_user_last_name = F('history_user__last_name'))
hist_filter_kwargs = dict(history_type__in=['~','+'])
hist_filter_args = []
to_html_kwargs = None
to_html_kwargs_extra = dict(formatters = {'salary': lambda val: f'${val:,.2f}'})
class PersonTable(tables.Table):
    ''' Table for displaying fixed Schedule instances '''
    hist = CollapseDataFrameColumn(
        accessor='history.all', values_args=hist_values_args, values_kwargs=hist_values_kwargs,
        filter_args=hist_filter_args, filter_kwargs=hist_filter_kwargs,
        annotate_kwargs=hist_annotate_kwargs,
        order_by_args=['-history_date'], limit=5,
        to_html_kwargs=to_html_kwargs, to_html_kwargs_extra=to_html_kwargs_extra
    )
    adjectives = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives') # regular iterable
    adjectives_links = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives W/links', hyperlink=True) # Iterable with links
    adjectives_dyn_labels = CollapseColumn(accessor='adjectives.all', iterable=True, verbose_name='Adjectives W/Dyn Labels', label_accessor='last_name') # iterable with dynamic labels
    pdict = CollapseColumn(accessor='attr_dict', dictionary=True, label_accessor='last_name') # dict 
    pdict_styled = CollapseColumn(accessor='attr_dict', dictionary=True, label_accessor='last_name', style='min-width:500px') # dict with style 
    longtxt = CollapseColumn(accessor='long_text', style='background-color: blue; color: yellow') # non-iterable using style
    org = CollapseColumn(accessor='org', label_accessor='org__name') # non-iterable with dynamic label
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True) # RoundNumberColumn
    delete = tables.LinkColumn('person-delete', verbose_name='', text='[Delete]', args=[A('id')])
    update = tables.LinkColumn('person-update', verbose_name='', text='[Update]', args=[A('id')])
    update_inline = tables.LinkColumn('person-update-inline', verbose_name='', text='[Update Inline]', args=[A('id')])
    class Meta:
        model = Person
        exclude = ['uuid']
        sequence = []


