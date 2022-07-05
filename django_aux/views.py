from django.shortcuts import render
from django_tables2 import SingleTableMixin
from django.shortcuts import redirect
from pandas import isna


class SaveFilterMixin(SingleTableMixin):
    """ This Mixin Can be used with a FilterView SingleTable in order to save
    the users filter selections after navegating away from the lookup page"""

    def get(self, request, *args, **kwargs):
        view_name = self.__class__
        qstr = self.request.GET.urlencode()
        full_path = request.get_full_path()

        if qstr != '':
            self.request.session[f'{view_name}_fp'] = full_path
            return super().get(request)
        else:
            fp = self.request.session.get(f'{view_name}_fp')
            if isna(fp) or '_export' in fp:
                return super().get(request)
            else:
                return redirect(fp)

    def get_filterset_kwargs(self, *args):
        kwargs = super().get_filterset_kwargs(*args)
        if 'clear_filter' in self.request.GET.keys():
            return {}
        else:
            return kwargs


