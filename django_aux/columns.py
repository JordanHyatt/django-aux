# python imports
import json, uuid
from math import ceil
from pandas import isna, Series, DataFrame as DF

# django imports
from django.utils.html import format_html, mark_safe, format_html_join
from django.db.models import QuerySet   

# 3rd party django
import django_tables2 as tables
from django_tables2 import A
from django.contrib.contenttypes.models import ContentType





from django_pandas.io import read_frame
from django_aux.utils import df_tz_convert



class FixedTextColumn(tables.Column):
    ''' Mimics behavior of django_tables2.tables.Column but allows for a fixed text to be rendered '''
    def __init__(self, *args, text='', empty_values=None, **kwargs):
        empty_values = empty_values or []
        super().__init__(*args, empty_values=empty_values, **kwargs)
        self.text = text

    def text_value(self, record, value, **kwargs):
        if self.text is None:
            return value
        return self.text(record) if callable(self.text) else self.text

    def value(self, record, value, **kwargs):
        return self.text_value(record=record, value=value, **kwargs)

    def render(self, record, value, **kwargs):
        return self.text_value(record=record, value=value, **kwargs)


class CheckFkColumn(tables.Column):
    ''' A column checks and displays the existence of a FK relationship '''
    def __init__(self, *args, fk_attr=None, present_symbol='✔', absent_symbol='X', **kwargs):
        super().__init__(*args, **kwargs)
        self.fk_attr = fk_attr if fk_attr.endswith('_id') else f'{fk_attr}_id'
        self.psym = present_symbol
        self.asym = absent_symbol

    def render(self, record, value, **kwargs):
        fk_obj = getattr(record, self.fk_attr)
        check = self.asym if fk_obj==None else self.psym
        return f'{value}{check}'

class RoundNumberColumn(tables.Column):
    """ A column that will round a number and add commas for display

    Args:
        *args: arguments to be passed to django-tables2 Column class __init__ method
        money: (bool default=False) Will append a dollar sign $ to front of value if true
        round_to: (int default=2) The number of decimals to round to
        prefix: (str, optional) This string is concatenated to the front of value
        suffix: (str, optional) This string is concatenated to the end of value
        orderable: (bool default=True) Can django-table sort/order this col. Will be set to false if money, suffix or prefix provided
        **kwargs: arguments to be passed to django-tables2 Column class __init__ method
    """    

    def __init__(self, *args, money=False, round_to=2, prefix='', suffix='', **kwargs):
        super().__init__(*args, **kwargs)
        self.money = money
        self.round_to = round_to
        self.prefix = prefix
        self.suffix = suffix
    
    def render(self, value, **kwargs):
        val = round(value, self.round_to)
        if self.round_to <= 0:
            rstr = f'{val:,.0f}'
        else:
            rstr = f'{val:,.{self.round_to}f}'
        if self.money: 
            rstr = '$' + rstr
        return self.prefix + rstr + self.suffix

    def value(self, value, record):
        ''' Overrides default value method (that would just call render on table export) '''
        return value
      
class CollapseColumnMixin:
    def __init__(
        self, 
        *args, 
        label='Show', label_accessor=None, label_extra='', style=None, nowrap=False, 
        empty_values=None, orderable=False,
        **kwargs   
    ):
        empty_values = empty_values or []
        super().__init__(*args, orderable=orderable, empty_values=empty_values, **kwargs)
        self.label = label
        self.label_accessor = label_accessor
        self.label_extra = label_extra
        self.style = style
        self.nowrap = nowrap


    def get_style(self):
        ''' method returns the style to be applied to the collapsable div '''
        if self.style:
            r = f'{self.style}'
        else:
            r = 'max-width: 25vw;'
        if self.nowrap:
            r += 'white-space: nowrap;'
        return f'"{r}"'

    def get_default_label(self, **kwargs):
        return self.label

    def get_label(self, val, record, value, **kwargs):
        """ A method that returns the label to be used for the collapasble div

        Args:
            value (str, optional): The value of the cell in the table (standard arg from django-tables2). Defaults to None.
            record (_type_, optional): The record representing the row of the table (standard arg from django-tables2). Defaults to None.
            val (_type_, optional): the html val to be rendered in the collapasable div. Defaults to None.

        Returns:
            str: The collapsable div label
        """        
        if self.label_accessor:
            rval = A(self.label_accessor).resolve(record, quiet=True) or self.get_default_label(val=val, record=record, value=value, **kwargs)
        else:
            rval = self.get_default_label(val=val, record=record, value=value, **kwargs)
        if hasattr(value, 'empty'): # hadle pd.DataFrame
            vbool = bool(value.empty)
        else:
            vbool = bool(value)
        if not vbool:
            return ''
        elif getattr(self, 'iterable', None):
            if len(value)==0:
                return ''            
        return str(rval) + self.label_extra

    def final_render(self, val, record, value, **kwargs):
        """ The final html to be rendered in the cell of the table

        Args:
            value (str, optional): The value of the cell in the table (standard arg from django-tables2). Defaults to None.
            record (_type_, optional): The record representing the row of the table (standard arg from django-tables2). Defaults to None.
            val (_type_, optional): the html val to be rendered in the collapasable div. Defaults to None.

        Returns:
            str: the html to be rendered in the cell of the table
        """        

        div_id = 'u' + str(uuid.uuid4()).replace('-','')
        label = self.get_label(val=val, record=record, value=value, **kwargs)
        if label != '':
            return format_html(
                '''<a href="#{}" data-toggle="collapse" aria-expanded="false" class="dropdown-toggle">
                    {}
                </a>
                <ul class="collapse list-styled" id="{}">
                    {}
                </ul>
                ''',
                div_id, label, div_id, val
            )
        else:
            return ''  

class CollapseColumnBase(CollapseColumnMixin, tables.Column):
    """ Sub-class of tables.Column with CollapseColumn functionality """


class CollapseJsonColumn(CollapseColumnMixin, tables.JSONColumn):
    """ Sub-class of JSONColumn with CollapseColumn functionality """

    def render(self, record, value, **kwargs):
        val = super().render(record, value)
        return self.final_render(val=val, record=record, value=value, **kwargs)


class CollapseUrlColumn(CollapseColumnMixin, tables.URLColumn):
    """ Sub-class of URLColumn with CollapseColumn functionality """

    def render(self, record, value, **kwargs):
        val = super().render(record, value, **kwargs)
        val = f'<a href={val}>{self.text}</a>'
        return self.final_render(val=val, record=record, value=value, **kwargs)


class CollapseDictColumn(CollapseColumnBase):
    """Custom django-tables2 column that will render a dictionary in a collapsable div.

    Args:
        *args (iterable, optional): arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
        *kwargs (iterable, optional): keyword arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
        label (str, optional): The string to be displayed on the collapse target. Defaults to "show"
        label_accessor (str, optional): Passed to django-tables2 Accessor object along with the cell value. 
            Result used as collapse target label
        label_extra (str, optional): Extra text that will be appended to the collapse target label
        style (str, optional): css expression that will be passed to the collapasable divs style parameter
        sort_by (str, optional): None, 'key' or 'value' determines what to sort the dictionary by. 
            keys and values will be pandas astype('string'). defaults to None. 
        ascending (bool, optional): bool that sorts keys/values ascending (True) or descending (False). Default = True
        na_position (str, optional): 'first' or 'last' places records with null values up front or at end respectively
        to_html_kwargs (dict, optional): kwargs to be passed to pd.DataFrame.to_html method. 
            defaults to dict(classes = ['table-bordered', 'table-striped', 'table-sm'], index=False, justify='left')   
        to_html_kwargs_extra (dict, optional): kwargs to be added to the to_html_kwargs (typically used for "adding" to defaults). Defaults to {}      
    """    
      
    def __init__(
        self, *args, 
        sort_by = None, 
        ascending = True, 
        na_position = 'last', 
        to_html_kwargs = None, 
        to_html_kwargs_extra = None, 
        **kwargs
    ):                
        super().__init__(*args, **kwargs)
        assert sort_by in [None, 'key', 'value'], 'Invalid sort_by arg. Options are None, key or value'
        self.sort_by = sort_by
        self.ascending = ascending
        self.na_position = na_position
        if to_html_kwargs==None:
            self.to_html_kwargs = dict(
                classes = ['table-bordered', 'table-striped', 'table-sm'],
                index=False, justify='left'
            )                    
        else: 
            self.to_html_kwargs = to_html_kwargs
        self.to_html_kwargs_extra = {} if to_html_kwargs_extra==None else to_html_kwargs_extra
        self.to_html_kwargs.update(self.to_html_kwargs_extra)
        
    def render(self, record, value, **kwargs):
        val = self.get_dictionary_html(record=record, value=value, **kwargs)        
        return self.final_render(value=value, record=record, val=val)

    def value(self, value, **kwargs):
        return value

    def get_dictionary(self, value, **kwargs):
        if isna(value):
            value = {}        
        if not isinstance(value, dict):
            try:
                value = json.loads(value)
            except ValueError:
                value = {}
        return value

    def get_dictionary_html(self, value, **kwargs):
        d = self.get_dictionary(value=value, **kwargs)
        df = DF(Series(d), columns=['value'])
        df = df.reset_index().rename(columns={'index':'key'})
        if self.sort_by:
            df = df.astype(
                {'value':'string','key':'string'}
            ).sort_values(self.sort_by, ascending=self.ascending, na_position=self.na_position)
        df_html = df.to_html(**self.to_html_kwargs)
        return format_html('<div style={}>{}</div>', mark_safe(self.get_style()), mark_safe(df_html))


class CollapseGenericForeignKey(CollapseDictColumn):

    def get_default_label(self, value, **kwargs):
        if not value:
            return
        return f'{value._meta.model.__name__} [{value.pk}]'

    def get_dictionary(self, record, value, **kwargs):
        if not value:
            return 
        model = value._meta.model
        content_type = getattr(record, 'content_type', None) or ContentType.objects.get_for_model(model)
        return {
            'App Label': content_type.app_label,
            'Model Name': model.__name__,
            'Object PK': value.pk,
            'Object': f'{value}'
        } 


class CollapseDataFrameColumn(CollapseColumnBase):
    """Custom django-tables2 column that will render a queryset as a pandas.DataFrame using the 
        pandas.DataFrame.to_html method in a collapsable div.

    Args:
        label (str, optional): text to be used on the collapse link. Defaults to 'Show'.
        group_by (bool, optional): Determines the order that values and annotate methods are applied to the qs. 
            If False: annoate then values. If True: values then annotate. Defaults to False.
        filter_args (list, optional): args passed to qs.filter method. Defaults to [].
        filter_kwargs (dict, optional): kwargs passed to qs.filter method. Defaults to {}.
        annotate_kwargs (dict, optional): kwargs passed to qs.annotate method. Ignored if use_read_frame=True.Defaults to {}.
        values_args (list, optional): args passed to qs.values method. Ignored if use_read_frame=True. Defaults to [].
        values_kwargs (dict, optional): args passed to qs.values method. Ignored if use_read_frame=True. Defaults to {}.
        order_by_args (list, optional): args passed to qs.order_by method. Defaults to [].
        limit (int, optional): limits the qs by slicing it qs[:limit]. Defaults to None.
        use_read_frame (bool, optional): Boolean indicating if django_pandas.io.read_frame
            should be used to convert the qs to a pandas.DataFrame. Defaults to True.
        fieldnames (list, optional): Passed to django_pandas.io.read_frame fieldnames kwarg. 
            ignored if user_read_frame==False. Defaults to None.
        column_names (list, optional): Passed to django_pandas.io.read_frame column_names kwarg. 
            ignored if user_read_frame==False. Defaults to None.
        to_html_kwargs (dict, optional): kwargs to be passed to df.to_html method. 
            Defaults to dict(classes = ['table-bordered', 'table-striped', 'table-sm'], index=False, justify='left').
        to_html_kwargs_extra (dict, optional): kwargs to be added to to_html_kwargs. Defaults to {}.
        timezone (str, optional): Timzone to use on tz-aware datetime columns. Defaults to settings.TIME_ZONE
        datetime_format (bool, optional): Whether to String format datetime columns. Defaults to True
        datetime_format_str (str, optional): What format to use on datetime columns. Defaults to %a %d %b %Y, %I:%M%p 
    """  
    def __init__(
        self, *args, 
        label='Show',
        group_by = False,
        filter_kwargs = None,
        filter_args = None, 
        annotate_kwargs = None, 
        values_kwargs = None, 
        values_args = None, 
        order_by_args = None, 
        limit = None, 
        use_read_frame = True, 
        fieldnames = None, 
        column_names = None,
        to_html_kwargs = None, 
        to_html_kwargs_extra = None, 
        timezone = None, 
        **kwargs   
    ):                
        super().__init__(*args, **kwargs)
        self.label = label
        self.limit = limit
        self.group_by = group_by
        self.timezone = timezone
        self.filter_kwargs = {} if filter_kwargs==None else filter_kwargs
        self.filter_args = [] if filter_args==None else filter_args
        self.annotate_kwargs = {} if annotate_kwargs==None else annotate_kwargs
        self.values_kwargs = {} if values_kwargs==None else values_kwargs
        self.values_args = [] if values_args==None else values_args
        self.order_by_args = [] if order_by_args==None else order_by_args
        self.use_read_frame = use_read_frame
        self.fieldnames = fieldnames
        self.column_names = column_names
        if to_html_kwargs==None:
            self.to_html_kwargs = dict(
                classes = ['table-bordered', 'table-striped', 'table-sm'],
                index=False, justify='left'
            )                    
        else: 
            self.to_html_kwargs = to_html_kwargs
        self.to_html_kwargs_extra = {} if to_html_kwargs_extra==None else to_html_kwargs_extra
        self.to_html_kwargs.update(self.to_html_kwargs_extra)
        self.no_wrap=False
         
    def get_read_frame_kwargs(self, **kwargs):
        """ Reuturns the kwargs to be passed to read_frame function """ 
        kwargs = {}
        if self.fieldnames:
            kwargs['fieldnames'] = self.fieldnames
        if self.column_names:
            kwargs['column_names'] = self.column_names
        return kwargs       

    def get_queryset(self, value, **kwargs):
        ''' method applies user passed kwargs/args to qs methods '''
        if not isinstance(value, QuerySet):
            return value
        qs = value.filter(
            *self.filter_args, **self.filter_kwargs
        )
        if self.use_read_frame == False:
            if self.group_by:
                qs = qs.values(
                    *self.values_args, **self.values_kwargs
                ).annotate(
                    **self.annotate_kwargs
                )
            else:
                qs = qs.annotate(
                    **self.annotate_kwargs
                ).values(
                    *self.values_args, **self.values_kwargs
                )
        qs = qs.order_by(*self.order_by_args)
        return qs if self.limit==None else qs[:self.limit]

    def get_df_final(self, qs, **kwargs):
        ''' Final steps to pd.DF before render or export '''
        if self.use_read_frame:
            df = read_frame(qs, **self.get_read_frame_kwargs())
        else:
            df = DF(qs)
            if self.column_names:
                df.columns = self.column_names
        df = df_tz_convert(df)
        return df

    def get_df_html(self, qs, **kwargs):
        df = self.get_df_final(qs)
        return df.to_html(**self.to_html_kwargs)

    def render(self, record, value, **kwargs):
        qs = self.get_queryset(value=value, **kwargs)
        if not qs:
            val = None
        elif qs.count() == 0: 
            val = None
        else:
            val = mark_safe(self.get_df_html(qs, **kwargs))
        return self.final_render(val=val, record=record, value=value, **kwargs)

    def value(self, value, **kwargs):
        ''' Return the value used during table export '''
        qs = self.get_queryset(value)
        if qs is None or qs.count() == 0:
            return None
        return self.get_df_final(qs).to_dict(orient='records')

class CollapseIterableColumn(CollapseColumnBase):
    """ Custom django-tables2 column that will render an iterable in a collapsable div.

    Args:
        *args (iterable, optional): arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
        order_items_by: (*fields, default None) Expression fed to order_by django method if iterable is a queryset. Should be comma separated fields or other order_by expressions
        hyperlink: (bool, default False) If true, will attempt to linkify the elements of the iterable
        fkwargs: (**kwargs, default None) Lookup/field parameters used in a Django Quereyset filter
        href_attr: (str, default None) Should be the name of an attribute or field that contains the url for linkified values
        str_attr: (str, default None) Name of attribute that will be used for display in lieu of value's __str__()
        **kwargs (iterable, optional): keyword arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
    """    

    def __init__(self, 
        *args, 
        order_items_by = None,
        hyperlink = False,
        fkwargs = None,
        href_attr = None, 
        str_attr = None,  
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.hyperlink = hyperlink
        self.href_attr = href_attr
        self.str_attr = str_attr
        self.order_items_by = order_items_by
        self.fkwargs = fkwargs

    def get_href(self, obj, **kwargs):
        ''' Method derives the href value to be used in hyperlinking list items '''
        if self.href_attr == None:
            return obj.get_absolute_url()
        else:
            return getattr(obj, self.href_attr)

    def get_prepped_value(self, value, **kwargs):
        if self.order_items_by and hasattr(value, 'order_by'):
            value = value.order_by(*self.order_items_by)
        if self.fkwargs:
            value = value.filter(**self.fkwargs)
        return value

    def get_final_value(self, value, **kwargs):
        value = self.get_prepped_value(value)
        val = mark_safe('')
        style = self.get_style()
        if not value:
            return ''
        for obj in value:
            obj_val = str(obj) if self.str_attr == None else getattr(obj, self.str_attr)
            if self.hyperlink:
                href = self.get_href(obj)
                obj_val = format_html('<a href={}>{}</a>', mark_safe(href), obj_val)
            val = val + format_html('<li style={}>{}</li>', mark_safe(style), obj_val)
        return val

    def render(self, record, value, **kwargs):
        val = self.get_final_value(value=value, **kwargs)
        if not val:
            return ''
        return self.final_render(val=val, record=record, value=value, **kwargs)

    def value(self, value, **kwargs):
        val = self.get_prepped_value(value)
        if self.str_attr:
            alt_values = []
            for obj in val:
                obj_val = getattr(obj, self.str_attr)
                alt_values.append(obj_val)
            return alt_values
        return list(val)

class CollapseNoniterableColumn(CollapseColumnBase):
    """ Custom django-tables2 column that will render an an object in a collapsable div.

    Args:
        *args (iterable, optional): arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
        hyperlink: (bool, default False) If true, will attempt to linkify the elements of the iterable
        href_attr: (str, default None) Should be the name of an attribute or field that contains the url for linkified values
        **kwargs (iterable, optional): keyword arguments to be passed to django_tables2 Column (See help(django_tables2.Column) for options)
    """   

    def __init__(self, *args, hyperlink=False, href_attr=None, orderable=True, **kwargs):
        super().__init__(*args, orderable=orderable, **kwargs)
        self.hyperlink = hyperlink
        self.href_attr = href_attr

    def get_href(self, obj, **kwargs):
        ''' Method derives the href value to be used in hyperlinking list items '''
        if self.href_attr == None:
            return obj.get_absolute_url()
        else:
            return getattr(obj, self.href_attr)

    def get_prepped_value(self, record, value, **kwargs):
        if self.hyperlink:
            href = self.get_href(record)
            val = format_html('<a href={}>{}</a>', mark_safe(href), value)
        else:
            val = value
        return format_html('<div style={}>{}</div>', mark_safe(self.get_style()), val)

    def render(self, record, value, **kwargs):
        val = self.get_prepped_value(value=value, record=record)
        return self.final_render(val=val, record=record, value=value, **kwargs)   

    def value(self, value, **kwargs):
        return value


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
