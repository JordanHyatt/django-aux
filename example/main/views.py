from django.shortcuts import render
from django.views.generic import TemplateView


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
