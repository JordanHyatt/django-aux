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
