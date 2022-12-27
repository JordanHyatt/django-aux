from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, DeleteView, CreateView, UpdateView
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin
from django_aux.views import SaveFilterMixin, RedirectPrevMixin, InlineFormsetMixin, PlotlyMixin
from main.tables import *
from main.filters import *
from main.models import *
from main.forms import *
from django.db.models.functions import TruncMonth, TruncWeek
from django.db.models import Sum, F, Q

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

class PersonLookup(PersonBase, ExportMixin, SaveFilterMixin, FilterView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Person Lookup'
        context['export_csv'] = True
        context.update(dict(url1='person-create', url1_text='[Create New Person]'))
        return context

class PersonCreate(PersonBase, RedirectPrevMixin, CreateView):
    form_class = PersonForm
    success_url = reverse_lazy('person-lookup')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Person Create'
        return context

class PersonDelete(PersonBase, RedirectPrevMixin, DeleteView):
    ''' Delete view for Person object '''
    template_name = 'django_aux/delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        href = reverse('person-update', kwargs=dict(pk=self.object.pk))
        emsg = f'* Usually it is better to de-activate the Person <a href={href}> here </a> *'
        context['extra_message'] = mark_safe(emsg)
        return context

class PersonUpdate(PersonBase, RedirectPrevMixin, UpdateView):
    ''' Update view for Person instance '''
    redirect_exceptions = ['delete']
    form_class = PersonForm


class PersonUpdateInline(PersonBase, InlineFormsetMixin, UpdateView):
    ''' Update view for Person instance '''
    template_name = 'django_aux/inline-formset.html'
    form_class = PersonForm
    form_helper = PersonHelper
    factories = [{'factory':award_factory, 'helper':PersonAwardHelper, 'header':'Awards'}]
    success_url = reverse_lazy('person-lookup')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_lines_btn'] = True
        return context


class SaleBase(MainBase):
    model = Sale
    table_class = SaleTable
    filterset_class = SaleFilter

class SaleLookup(SaleBase, ExportMixin, SaveFilterMixin, FilterView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Sale Lookup'
        context['export_csv'] = True
        return context

class SalePlotly(SaleBase, PlotlyMixin ,SaveFilterMixin, FilterView):
    filterset_class = SalePlotlyFilter
    template_name = 'django_aux/standard-plotly.html'
    plot_width = 1200
    plot_height = 500
    X_CHOICES = [ ('category','Sale Category'), ('buyer', 'Buyer'), ('month', 'Month'), ('week', 'Week')]


    CHOICE_VALUES_MAP = {
        'category': 'category',
        'buyer':'buyer',
        'week': dict(week=TruncWeek('dtg')),
        'month': dict(month=TruncMonth('dtg')),
    }
    Y_CONFIG = {
        'total_sales' : {
            'verbose': 'TotalSales',
            'agg_expr':  Sum('amount'),
        }
    }


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Sale Data Exploration'
        print(context.get('some_var'))
        return context


class SaleDelete(SaleBase, RedirectPrevMixin, DeleteView):
    template_name = 'django_aux/delete.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['extra_message'] = 'This is an extra message'
        return context