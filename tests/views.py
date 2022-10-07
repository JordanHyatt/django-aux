from django_filters.views import FilterView
from django_aux.views import SaveFilterMixin
from .tables import *
from .filters import *
from .models import *
from .forms import *




class PersonLookup(SaveFilterMixin, FilterView):
    model = Person
    table_class = PersonTable
    filterset_class = PersonFilter
    template_name = "test.html"