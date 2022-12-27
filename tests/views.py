from django_filters.views import FilterView
from django_aux.views import SaveFilterMixin, RedirectPrevMixin
from django.views.generic import CreateView
from .tables import *
from .filters import *
from .models import *
from .forms import *


class PersonLookup(SaveFilterMixin, FilterView):
    model = Person
    table_class = PersonTable
    filterset_class = PersonFilter
    template_name = "test.html"


class PersonCreate(RedirectPrevMixin, CreateView):
    model = Person
    form_class = PersonForm
    redirect_exceptions = [('person-delete', 'person-lookup')]
    template_name = "test.html"

class PersonCreateWithRequest(RedirectPrevMixin, CreateView):
    model = Person
    form_class = PersonFormWithRequest
    template_name = "test.html"
    


