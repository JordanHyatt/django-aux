from .models import Person
from django_aux.filters import FilterSetBase, MetaBase
from crispy_forms.layout import *


class PersonFilter(FilterSetBase):
    ''' A filter for Person objects '''
    class Meta(MetaBase):
        model = Person
        fields = {
            'last_name': ['icontains'],
            'first_name': ['icontains'],
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper.layout = Layout(
            Fieldset('',
                Row(
                    Div('last_name__icontains', css_class='ml-2 col-flex'),
                    Div('first_name__icontains', css_class='ml-2 col-flex'),
                ),
            ),
        ) 