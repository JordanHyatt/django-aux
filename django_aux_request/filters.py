from django_aux.filters import FilterSetBase, MetaBase
from request.models import Request
from crispy_forms.layout import Layout, Fieldset, Row, Div



class RequestFilter(FilterSetBase):
    ''' A filter for Request objects '''
    
    class Meta(MetaBase):
        model = Request
        fields = {
            'response': ['icontains'],
            'method': ['icontains'],
            'path': ['icontains'],
            'is_secure': ['exact'],
            'ip': ['icontains'],
            'user__username': ['icontains'],
            'referer': ['icontains'],
            'time':['gte', 'lte']
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['time__gte'].label = 'Received after:'
        self.form.fields['time__lte'].label = 'Received before:'
        self.base_layout = Layout(
            Fieldset('',
                Row(
                    Div('response__icontains', css_class='ml-2 col-flex'),
                    Div('method__icontains', css_class='ml-2 col-flex'),
                    Div('path__icontains', css_class='ml-2 col-flex'),
                    Div('is_secure', css_class='ml-2 col-flex'),
                    Div('ip__icontains', css_class='ml-2 col-flex'),
                    Div('user__username__icontains', css_class='ml-2 col-flex'),
                    Div('referer__icontains', css_class='ml-2 col-flex'),
                ),
                Row(
                    Div('time__gte', css_class='ml-2 col-flex'),
                    Div('time__lte', css_class='ml-2 col-flex'),
                ),
            ),
        )
        self.form.helper.layout = self.base_layout