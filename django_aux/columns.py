import django_tables2 as tables
from django_tables2 import A
import random
from pandas import isna
import json
from django.utils.html import format_html


class CollapseColumn(tables.Column):
    ''' Column is meant for columns that have lots of data in each cell to make 
    viewing cleaner'''

    def __init__(
        self, *args, label='Show', label_accessor=None, label_extra='', hyperlink=False, href_attr=None,
        iterable=False, str_attr=None, order_by=None, fkwargs=None, property_attr=None, dictionary=False,
        nowrap=True, li_style=None,
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
        self.fkwargs = fkwargs
        self.property_attr = property_attr
        self.dictionary = dictionary
        if self.dictionary:
            self.iterable = True

    def get_label(self, record):
        if self.label_accessor:
            rval = A(self.label_accessor).resolve(record)
        else:
            rval = self.label
        return str(rval) + self.label_extra

    def get_href(self, obj):
        ''' Method derives the href value to be used in hyperlinking list items '''
        if self.href_attr == None:
            return obj.get_absolute_url()
        else:
            return getattr(obj, self.href_attr)

    def get_li_style(self):
        ''' method returns the style to be applied to the li tags '''
        if self.li_style:
            return self.li_style
        return 'style="white-space: nowrap;"' if self.nowrap else ''

    def render(self, value, record):
        if self.property_attr:
            value = getattr(record, self.property_attr)
        randnum = random.randint(1, 1_000_000_000)
        label = self.get_label(record)
        if self.iterable == False:
            if isna(value) or value == '' or value == {}:
                label = ''
            if self.hyperlink:
                val = f'<a href={value}>{value}</a>'
            else:
                val = value
        else:
            if self.dictionary:
                if type(value) != dict:
                    value = json.loads(value)
                if isna(value):
                    value = {}
                value = value.items()
            if self.order_by:
                value = value.order_by(self.order_by)
            if self.fkwargs:
                value = value.filter(**self.fkwargs)
            if len(value) == 0:
                label = ''
            val = ''
            style = self.get_li_style()
            for obj in value:
                obj_val = str(obj) if self.str_attr == None else getattr(
                    obj, self.str_attr)
                val = val + f'<li {style}>{obj_val}</li>'
                if self.hyperlink:
                    href = self.get_href(obj)
                    obj_val = f'<a href={href}>{obj_val}</a>'
                val = val + f'<li style="white-space: nowrap;">{obj_val}</li>'
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
