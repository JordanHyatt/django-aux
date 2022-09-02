from django_aux.filters import FilterSetBase, MetaBase
from main.models import *
from django_aux.filters import PlotSettingsFilterMixin
from crispy_forms.layout import *


class PersonFilter(FilterSetBase):
    ''' A filter for Person objects '''
    class Meta(MetaBase):
        model = Person
        fields = {
            'last_name': ['icontains'],
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper.layout = Layout(
            Fieldset('',
                Row(
                    Div('last_name__icontains', css_class='ml-2 col-flex'),
                ),
            ),
        ) 


class SaleFilter(FilterSetBase):
    ''' A filter for Sale objects '''
    class Meta(MetaBase):
        model = Sale
        fields = {
            'buyer__last_name': ['icontains'],
            'dtg': ['gte','lte']
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_layout = Layout(
            Fieldset('',
                Row(
                    Div('buyer__last_name__icontains', css_class='ml-2 col-flex'),
                ),
                Row(
                    Div('dtg__gte',css_class='ml-2 col-flex'),
                    Div(HTML('-->'),style="margin-top:25px"),
                    Div('dtg__lte',css_class='col-flex'),
                )
            ),
        )
        self.form.helper.layout = self.base_layout 


class SalePlotlyFilter(PlotSettingsFilterMixin, SaleFilter):
    ''' A filter for Sale objects '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper.layout = Layout(self.base_layout, self.extra_layout)