from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, DeleteView, CreateView, UpdateView, FormView
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin
from django_tables2 import SingleTableMixin
from django.http import HttpResponseRedirect
from django_aux.views import SaveFilterMixin, RedirectPrevMixin, InlineFormsetMixin, PlotlyMixin, DeleteProtectedView
from main.tables import *
from main.filters import *
from main.models import *
from main.forms import *
from django.db.models.functions import TruncMonth, TruncWeek
from django.db.models import Sum, Avg, F, Q

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
        context.update(dict(url2='person-create-inline', url2_text='[Create New Person Inline]'))
        return context

class PersonCreate(PersonBase, RedirectPrevMixin, CreateView):
    form_class = PersonForm
    success_url = reverse_lazy('person-lookup')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Person Create'
        return context

class PersonDelete(PersonBase, RedirectPrevMixin, DeleteProtectedView):
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
    redirect_exceptions = [('delete','person-lookup')]
    form_class = PersonForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_js'] = ['main/hello.js'] 
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cancel_on_click'] = f"window.location.href='{reverse_lazy('person-create')}';"
        return kwargs

class PersonUpdateInline(PersonBase, SingleTableMixin, InlineFormsetMixin, UpdateView):
    ''' Update view for Person instance '''
    template_name = 'django_aux/inline-formset.html'
    form_class = PersonForm
    form_helper = PersonHelper
    factories = [{'factory':award_factory, 'helper':PersonAwardHelper, 'header':'Awards'}]
    success_url = reverse_lazy('person-lookup')
    table_class = PersonTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_lines_btn'] = True
        context['table_header'] = 'Look at my awesome table!'
        context['cancel_btn_value'] = f"Person Lookup"
        context['cancel_on_click'] = f"window.location.href='{reverse_lazy('person-lookup')}';"
        return context

class PersonCreateInline(PersonBase, InlineFormsetMixin, CreateView):
    template_name = 'django_aux/inline-formset.html'
    form_class = PersonForm
    form_helper = PersonHelper
    factories = [{'factory':award_factory, 'helper':PersonAwardHelper, 'header':'Awards'}]
    success_url = reverse_lazy('person-lookup')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Person Create'
        context['cancel_btn_value'] = f"Person Lookup"
        context['cancel_on_click'] = f"window.location.href='{reverse_lazy('person-lookup')}';"
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


class SaleLookupButtons(SaleBase, ExportMixin, SaveFilterMixin, FilterView):
    template_name = 'django_aux/form-table.html'

    def get_submit_buttons(self):
        return [
            {'name':'delete', 'display':'Delete Selected Objects'},
            {'name':'make_misc', 'display':'Change Category to Misc'},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Sale Lookup'
        context['export_csv'] = True
        context['checkbox_col_name'] = 'checked_id'
        context['submit_buttons'] = self.get_submit_buttons()
        return context

    def post(self, request, *args, **kwargs):
        qs = Sale.objects.filter(id__in=request.POST.getlist('checked_id'))
        if 'delete' in request.POST:
            qs.delete()
            
        if 'make_misc' in request.POST:
            for obj in qs.exclude(category='misc'):
                obj.category = 'misc'
                obj.save()

        return HttpResponseRedirect(reverse('sale-lookup-buttons'))



class SaleLookupWithForm(SaleBase, ExportMixin, SaveFilterMixin, FilterView):
    template_name = 'django_aux/form-table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Sale Lookup'
        context['export_csv'] = True
        context['checkbox_col_name'] = 'checked_id'
        context['form'] = SaleTableForm()
        context['form_action'] = reverse('sale-lookup-handle-form')
        return context

class SaleLookupHandleForm(SaleBase, FormView):
    form_class = SaleTableForm
    success_url = 'sale-lookup-form'

    def form_valid(self, form):
        cd = form.cleaned_data
        print(cd)
        print(self.request.POST)
        return super().form_valid(form)


class SalePlotly(SaleBase, PlotlyMixin ,SaveFilterMixin, FilterView):
    filterset_class = SalePlotlyFilter
    template_name = 'django_aux/standard-plotly.html'
    plot_width = 1200
    plot_height = 500
    plot_title = 'Sales Data Explorer'
    include_id_in_agg_choices = True


    X_CHOICES = [ ('category','Sale Category'), ('buyer', 'Buyer'), ('month', 'Month'), ('week', 'Week')]
    

    CHOICE_VALUES_MAP = {
        'category': 'category',
        'buyer':'buyer',
        'week': dict(week=TruncWeek('dtg')),
        'month': dict(month=TruncMonth('dtg')),
    }
    Y_CONFIG = {
        'total_sales' : {
            'verbose': 'Total Sales',
            'agg_expr':  Sum('amount'),
        },
        'average_sales' : {
            'verbose': 'Avg Sale Amount',
            'agg_expr':  Avg('amount'),
        },
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