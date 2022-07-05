from django_aux.filters import BaseFilterSet, MetaBase
from main.models import Person
from crispy_forms.layout import *


class PersonFilter(BaseFilterSet):
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
