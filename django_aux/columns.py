import django_tables2 as tables
from django_tables2 import A
import random
from pandas import isna, Series, DataFrame as DF
from math import ceil
import json
from django.utils.html import format_html


class CheckFkColumn(tables.Column):
    ''' A column checks and displays the existence of a FK relationship '''
    def __init__(self, *args, fk_attr=None, present_symbol='✔', absent_symbol='X', **kwargs):
        super().__init__(*args, **kwargs)
        self.fk_attr = fk_attr if fk_attr.endswith('_id') else f'{fk_attr}_id'
        self.psym = present_symbol
        self.asym = absent_symbol

    def render(self, value, record):
        fk_obj = getattr(record, self.fk_attr)
        check = self.asym if fk_obj==None else self.psym
        return f'{value}{check}'

class RoundNumberColumn(tables.Column):
    ''' A column that will round a number and add commas for display '''

    def __init__(self, *args, money=False, round_to=2, prefix='', **kwargs):
        super().__init__(*args, **kwargs)
        self.money = money
        self.round_to = round_to
        self.prefix = prefix
    
    def render(self, value, record):
        val = round(value, self.round_to)
        if self.round_to <= 0:
            rstr = f'{val:,.0f}'
        else:
            rstr = f'{val:,.{self.round_to}f}'
        if self.money: 
            rstr = '$' + rstr
        return self.prefix + rstr


class CollapseColumn(tables.Column):
    ''' Column is meant for columns that have lots of data in each cell to make viewing cleaner'''

    def __init__(
        self, *args, label='Show', label_accessor=None, label_extra='', hyperlink=False, href_attr=None,
        iterable=False, str_attr=None, order_by=None, fkwargs=None, property_attr=None, dictionary=False,
        nowrap=True, style=None,
        **kwargs
    ):  # Note on kwargs: lavel_accessor used to make dynamic labels, label_extra is a str that adds on to the returned value
        super().__init__(*args, **kwargs)
        self.label = label
        self.label_accessor = label_accessor
        self.label_extra = label_extra
        self.hyperlink = hyperlink  # Attempts to linkify the elements of an iterable
        # the attribute name to be used to pull the href value if None provided get_absolute_url will be called
        self.href_attr = href_attr
        self.iterable = iterable
        self.str_attr = str_attr
        self.order_by = order_by
        self.nowrap = nowrap
        self.style = style
        self.fkwargs = fkwargs
        self.property_attr = property_attr
        self.dictionary = dictionary

    def get_label(self, value=None, record=None):
        if self.label_accessor:
            rval = A(self.label_accessor).resolve(record)
        else:
            rval = self.label
        if value in [None, {}]:
            return ''     
        elif self.iterable:
            if len(value)==0:
                return ''            
        return str(rval) + self.label_extra

    def get_href(self, obj):
        ''' Method derives the href value to be used in hyperlinking list items '''
        if self.href_attr == None:
            return obj.get_absolute_url()
        else:
            return getattr(obj, self.href_attr)

    def get_style(self):
        ''' method returns the style to be applied to the li tags '''
        if self.style:
            return f'"{self.style}"'
        return '"white-space: nowrap;"' if self.nowrap else ''

    def render(self, value, record):
        if self.property_attr:
            value = getattr(record, self.property_attr)
        if self.dictionary:
            val = self.get_dictionary_val(value=value)        
        elif self.iterable == False:
            val = self.get_noniterable_val(value=value, record=record)
        else: 
            val = self.get_iterable_val(value)
        return self.final_render(value=value, record=record, val=val)
   
    def final_render(self, value, record, val):
        randnum = random.randint(1, 1_000_000_000)
        label = self.get_label(value=value, record=record)
        if label != '':
            rval = (
                f'''
                <a href="#unique{record.pk}{randnum}" data-toggle="collapse" aria-expanded="false" class="dropdown-toggle">
                    {label}
                </a>
                <ul class="collapse list-styled" id="unique{record.pk}{randnum}">
                    {val}
                </ul>
                '''
            )
            return format_html(rval)
        else:
            return ''
    
    def get_iterable_val(self, value):
        if self.order_by:
            value = value.order_by(self.order_by)
        if self.fkwargs:
            value = value.filter(**self.fkwargs)
        val = ''
        style = self.get_style()
        for obj in value:
            obj_val = str(obj) if self.str_attr == None else getattr(obj, self.str_attr)
            if self.hyperlink:
                href = self.get_href(obj)
                obj_val = f'<a href={href}>{obj_val}</a>'
            val = val + f'<li style={style}>{obj_val}</li>'
        return val

    def get_noniterable_val(self, value, record):
        if self.hyperlink:
            href = self.get_href(record)
            val = f'<a href={href}>{value}</a>'
        else:
            val = value
        return f'<div style={self.get_style()}>{val}</div>'

    def get_dictionary_val(self, value):
        if isna(value):
            value = {}        
        if type(value) != dict:
            value = json.loads(value)
        df = DF(Series(value), columns=['value'])
        df = df.reset_index().rename(columns={'index':'key'})
        df_html = df.to_html(
            classes = ['table-bordered', 'table-striped', 'table-sm'],
            index=False, justify='left', header=False
        )
        return f'<div style={self.get_style()}>{df_html}</div>'


def get_background(value, record, table, bound_column):
    val = (str(value).split('/')[0]).replace(',','')
    val = float(val)
    vals = [getattr(row, bound_column.name) for row in table.data]
    ser = Series(vals).fillna(0)
    max = ser.max()
    if max == 0:
        w = 0
    else:
        w = 100*val/max
    style_str = f'background:linear-gradient(90deg, {bound_column.column.color} {w}%, transparent {w}%)'
    return style_str
class BarChartColumn(tables.Column):
    def __init__(
        self, *args,
        round_to=0,
        color='lightgrey',
        goal_attr=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.round_to = round_to
        self.color = color
        self.goal_attr = goal_attr
        td_dict = self.attrs.get('td', {})
        td_dict['style'] = get_background
        self.attrs['td'] = td_dict

    def render(self, value, record):
        if value==None:
            return
        value = round(value, self.round_to)
        if self.round_to > 0:
            rval = f'{value:,}'
        else:
            rval = f'{value:,.0f}'

        if self.goal_attr:
            goal = getattr(record, self.goal_attr, '')
            goal = ceil(goal)
            rval = str(rval) + f'/{goal}'
        return rval

    def value(self, value):
        value = str(value).split('/')[0]
        if not str(value).isnumeric():
            value = 0
        return value


class LastChangeDateColumn(tables.Column):
    ''' This Column can be used with tables that have a model defined and 
    are using django simple-history to track changes'''

    def render(self, record):
        if not hasattr(record, 'history'):
            return None
        else:
            return record.history.first().history_date


class LastChangeUserColumn(tables.Column):
    ''' This Column can be used with tables that have a model defined and 
    are using django simple-history to track changes'''

    def render(self, record):
        if not hasattr(record, 'history'):
            return None
        else:
            user = record.history.first().history_user
            if user == None:
                return 'Automated'
            return user.employee


class LastChangeTypeColumn(tables.Column):
    ''' This Column can be used with tables that have a model defined and 
    are using django simple-history to track changes'''

    def render(self, record):
        if not hasattr(record, 'history'):
            return None
        else:
            return record.history.first().history_type