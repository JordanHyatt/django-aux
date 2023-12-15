from django_aux.filters import FilterSetBase, MetaBase
from crispy_forms.layout import Layout, Fieldset, Row, Div

from .models import Country, Subdivision, Address


class CountryFilter(FilterSetBase):
    class Meta(MetaBase):
        model = Country
        fields = {
            'alpha2': ['exact'],
            'alpha3': ['exact'],
            'name': ['icontains'],

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper.layout = Layout(
            Fieldset('',
                Row(
                    Div('alpha2', css_class='ml-2 col-flex'),
                    Div('alpha3', css_class='ml-2 col-flex'),
                    Div('name__icontains', css_class='ml-2 col-flex'),
                ),
            ),
        ) 


