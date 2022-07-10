from django.shortcuts import render
from django.views.generic import TemplateView, DeleteView, CreateView, UpdateView
from django_filters.views import FilterView
from django_aux.views import SaveFilterMixin, RedirectPrevMixin
from main.tables import *
from main.filters import *
from main.models import *


class MainBase:
    ''' A base view for main app that implements common methods '''
    paginate_by = 50
    template_name = "django_aux/standard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = '------- Main Portal --------'
        context['extend_str'] = 'main/base.html'
        return context

class HomePageView(MainBase, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Select Option From Side Bar'
        return context


class PersonBase(MainBase):
    model = Person
    table_class = PersonTable
    filterset_class = PersonFilter

class PersonLookup(PersonBase, SaveFilterMixin, FilterView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Person Lookup'
        return context

class PersonDelete(PersonBase, RedirectPrevMixin, DeleteView):
    ''' Delete view for Person object '''
    template_name = 'django_aux/delete.html'
