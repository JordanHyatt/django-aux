from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from django import forms
from django_aux.forms import BaseModelForm
from main.models import *

class PersonForm(BaseModelForm):
    class Meta:
        model = Person
        exclude = []