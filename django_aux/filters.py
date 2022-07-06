from django_filters import *
import django.db.models as models
from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput
from crispy_forms.helper import FormHelper
from django import forms
from crispy_forms.layout import *


class MetaBase:
    filter_overrides = {
        models.DateTimeField: {
            'filter_class': DateTimeFilter,
            'extra': lambda f: {
                'widget': DateTimePickerInput,
            },
        },
        models.DateField: {
            'filter_class': DateFilter,
            'extra': lambda f: {
                'widget': DatePickerInput,
            },
        },
        models.BooleanField: {
            'filter_class': MultipleChoiceFilter,
            'extra': lambda f: {
                'widget': forms.CheckboxSelectMultiple,
                'choices': ((True, 'Yes'), (False, 'No'))
            },
        },
    }

class BaseFilterSet(FilterSet):
    ''' A BaseFilter class that initializes a crispy form helper 
    with submit and clear filter buttons '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.add_input(
            Submit('submit', 'Apply Filter')
        )
        self.form.helper.add_input(
            Submit('clear_filter', 'Clear Filter', css_class='btn-warning')
        )



class PlotSettingsFilterMixin(FilterSet):
    ''' The purpose of this filter is to add in a standard form for plot
    settings to a normal model filter'''

    def filter_queryset(self, queryset):
        qdict = self.form.cleaned_data.copy()
        for key in ['x', 'y', 'plot_type', 'color', 'aggregate_by', 'N_min']:
            if key in qdict.keys():
                qdict.pop(key)
        for name, value in qdict.items():
            if value in ['', None, []]:
                continue
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(queryset, models.QuerySet), \
                "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                % (type(self).__name__, name, type(queryset).__name__)
        return queryset

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices == None:
            choices = dict(
                X_CHOICES=(('quarter', 'Quarter'), ('month', 'Month'),
                           ('week', 'Week'), ('day', 'Day')),
                Y_CHOICES=[],
                COLOR_CHOICES=[],
                PLOT_TYPE_CHOICES=(
                    ('barg', 'Bar-Grouped'), ('bars', 'Bar-Stacked'),
                    ('line', 'Line'), ('scatter', 'Scatter'),
                    ('box', 'Box'), ('violin', 'Violin'),
                ),
                AGG_CHOICES=(
                    (None, '--------'),
                    ('quarter', 'Quarter'), ('month',
                                             'Month'), ('week', 'Week'), ('day', 'Day')
                )
            )
        self.form.fields['x'] = forms.ChoiceField(
            choices=choices.get('X_CHOICES'))
        self.form.fields['y'] = forms.ChoiceField(
            choices=choices.get('Y_CHOICES'))
        self.form.fields['plot_type'] = forms.ChoiceField(
            choices=choices.get('PLOT_TYPE_CHOICES'))
        self.form.fields['color'] = forms.ChoiceField(
            choices=choices.get('COLOR_CHOICES'), required=False)
        self.form.fields['aggregate_by'] = forms.ChoiceField(
            choices=choices.get('AGG_CHOICES'), required=False)
        self.form.fields['N_min'] = forms.IntegerField(
            initial=0, required=False, label='Sample Size Min')
        self.extra_layout = Layout(
            Fieldset('Plot Settings',
                Row(
                    Div('aggregate_by', css_class='ml-2 col-flex'),
                    Div('x', css_class='ml-2 col-flex'),
                    Div('y', css_class='ml-2 col-flex'),
                    Div('color', css_class='ml-2 col-flex'),
                    Div('plot_type', css_class='ml-2 col-flex'),
                    Div('N_min', css_class='ml-2 col-flex',
                        style='width:175px'),
                ),
            ),
        )


