from django_aux.forms import ModelFormBase
from .models import Person

class PersonFormWithRequest(ModelFormBase):
    class Meta:
        model = Person
        exclude = []

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        
class PersonForm(ModelFormBase):
    class Meta:
        model = Person
        exclude = []