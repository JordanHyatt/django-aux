import django_tables2 as tables
from django.db.models import F, Q, Sum
from django_tables2 import A
from main.models import *
from django_aux.columns import (
    CollapseColumn, RoundNumberColumn, CollapseDataFrameColumn, CollapseDictColumn, 
    CollapseIterableColumn, CollapseNoniterableColumn, FixedTextColumn
)
from django.urls import reverse_lazy

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
        use_read_frame=False,
        accessor='history.all', values_args=hist_values_args, values_kwargs=hist_values_kwargs,
        filter_args=hist_filter_args, filter_kwargs=hist_filter_kwargs,
        annotate_kwargs=hist_annotate_kwargs,
        order_by_args=['-history_date'], limit=10,
        to_html_kwargs=to_html_kwargs, to_html_kwargs_extra=to_html_kwargs_extra
    )
    hist_agg = CollapseDataFrameColumn(
        accessor='history.all', 
        use_read_frame = False,
        group_by = True,
        values_kwargs=dict(org_name = F('org__name')),
        annotate_kwargs=dict(salary_sum = Sum('salary')),
        to_html_kwargs=to_html_kwargs, to_html_kwargs_extra=to_html_kwargs_extra,
        order_by_args=['org_name'],
    )
    hist_read_frame = CollapseDataFrameColumn(
        accessor='history.all', values_args=hist_values_args, values_kwargs=hist_values_kwargs,
        filter_args=hist_filter_args, filter_kwargs=hist_filter_kwargs,
        order_by_args=['-history_date'],
        use_read_frame=True, limit=10,
        fieldnames=['history_id', 'history_user', 'history_relation__adjectives__word'],
        column_names=['history_id', 'history_user', 'adjective'],
        to_html_kwargs=to_html_kwargs, to_html_kwargs_extra=to_html_kwargs_extra,
    )
    salary = CollapseNoniterableColumn(accessor='salary')
    middle_name = CollapseNoniterableColumn(accessor='middle_name', hyperlink=True, href_attr='foo_url')
    adjectives = CollapseIterableColumn(accessor='adjectives.all', verbose_name='Adjectives') # regular iterable
    awards = CollapseIterableColumn(accessor='personaward_set.all', verbose_name='Awards') # regular iterable
    adjectives_links = CollapseIterableColumn(accessor='adjectives.all', verbose_name='Adjectives W/links', hyperlink=True) # Iterable with links
    adjectives_dyn_labels = CollapseIterableColumn(accessor='adjectives.all', verbose_name='Adjectives W/Dyn Labels', label_accessor='last_name') # iterable with dynamic labels
    pdict = CollapseDictColumn(
        accessor='attr_dict', label_accessor='last_name', sort_by='value', ascending=False
    ) # dict sorted by desc value
    pdict_styled = CollapseDictColumn(
        accessor='attr_dict', label_accessor='last_name', style='min-width:500px', sort_by='key', 
        to_html_kwargs = dict(
                classes = ['table-lg'],
                index=False, justify='center'
        )
    ) # dict with style, sorted by key, custom style
    longtxt = CollapseColumn(accessor='long_text', style='background-color: blue; color: yellow; min-width:50vw') # non-iterable using style
    org = CollapseColumn(accessor='org', orderable=True, label_accessor='org__name') # non-iterable with dynamic label
    salary_rounded = RoundNumberColumn(accessor='salary', round_to=0, money=True) # RoundNumberColumn
    delete = tables.LinkColumn('person-delete', verbose_name='', text='[Delete]', args=[A('id')])
    update = tables.LinkColumn('person-update', verbose_name='', text='[Update]', args=[A('id')])
    update_inline = tables.LinkColumn('person-update-inline', verbose_name='', text='[Update Inline]', args=[A('id')])
    fixed_text = FixedTextColumn(text='Im a fixed label', linkify=lambda: '#', verbose_name='Fixed Text Header')
    class Meta:
        model = Person
        exclude = ['uuid']
        sequence = []

class SaleTable(tables.Table):
    amount = RoundNumberColumn(round_to=2, money=True)
    salary_percent = RoundNumberColumn(accessor='percent_of_million', suffix='%', orderable=False)
    delete = FixedTextColumn(text='[Delete]', verbose_name='', linkify = lambda record: reverse_lazy('sale-delete', kwargs={'pk': record.pk}))
    checked_id = tables.CheckBoxColumn(accessor='id', attrs = {"th__input": {"onclick": "toggle(this)"}})
    class Meta:
        model = Sale
        exclude = []
        sequence = ['checked_id']

    


