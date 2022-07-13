from django_tables2 import SingleTableMixin
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from pandas import isna, DataFrame as DF, to_datetime
import inspect
from django.contrib import messages
from django.db.models import F
from django_pandas.io import read_frame
from django.contrib.auth.mixins import UserPassesTestMixin
import plotly.express as px
from plotly import offline

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

class InlineFormsetMixin:
    formset_helper = None
    form_helper = None
    
    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data(*args,**kwargs)
        if self.request.POST:
            context['formset'] = self.formset(self.request.POST,instance=self.object)
        else:
            context['formset'] = self.formset(instance=self.object)
        context['formset_helper']=self.formset_helper if self.formset_helper else None
        context['form_helper']=self.form_helper if self.form_helper else None
        return context               
        
    def post(self, request, *args, **kwargs):
        next = self.request.session.get('next')
        cancel = 'cancel' in self.request.POST.keys()
        print(cancel,next)
        if next and cancel:
            return HttpResponseRedirect(next)
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None
        context = self.get_context_data()
        form = self.get_form()
        child = context['formset']
        if form.is_valid() and child.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self,form):
        self.object = form.save()
        context = self.get_context_data()
        children_names = ['formset']
        for children_name in children_names:
            child = context[children_name] 
            child.is_valid()
            child.save()
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        if 'addlines' in self.request.POST:
            return self.request.path_info
        else:
            return super().get_success_url()

class SaveFormMixin:
    """ This Mixin Can be used with any view that uses a form mixin to
    save a users form selection even if they navigate away from the page"""
    ignore_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_name = self.__class__

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        if self.request.method == 'GET':
            if len(self.request.GET) > 0:
                qd = self.request.GET
                self.request.session[f'{self.view_name}_form_initial'] = qd
            initial = self.request.session.get(
                f'{self.view_name}_form_initial')
            if initial not in [{}, None]:
                for field in self.ignore_fields:
                    if field in initial.keys():
                        initial.pop(field)
                form = self.form_class(initial=initial)

        if self.request.method == 'POST':
            self.request.session[f'{self.view_name}_form_initial'] = form.data

        return form

class RedirectPrevMixin:
    ''' This mixin will redirect user to the page they came from if 
    form successful OR if "cancel" is in post data  (Uses session data)'''

    @property
    def form_takes_request_arg(self):
        ''' Property returns True if any of the Parent classes of the views form_class take an 
        argument "request" to their consctructor '''
        form_class = getattr(self.__class__, 'form_class')
        if not form_class: return
        for base in inspect.getmro(form_class):
            if 'request' in inspect.signature(base.__init__).parameters.keys():
                return True
        return False

    def get_form_kwargs(self, *args, **kwargs):
        ''' Method inserts request into the forms kwargs *IF* the forms constructor allows for it '''
        if not self.form_takes_request_arg:
            return super().get_form_kwargs()
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        ''' Extends the get method to store where the user was prior to this page '''
        next = self.request.META.get('HTTP_REFERER')
        if next == None: 
            next = ''
        mask = request.path in next # redirected from the same page, dont overrwrite next
        if not mask:
            request.session['next'] = self.request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        ''' If next was stored redirect there, otherwise return super() '''
        next = self.request.session.get('next')
        m = 'addlines' not in self.request.POST # 
        if next and m: 
            return next
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        ''' Override post method to redirect to "next" *IF* 'cancel' is present 
        in POST and next is defined in user session '''
        next = self.request.session.get('next')
        cancel = 'cancel' in self.request.POST.keys()
        if next and cancel:
            return HttpResponseRedirect(next)
        else:
            return super().post(request, *args, **kwargs)

class CheckGroupPermMixin(UserPassesTestMixin):
    ''' This mixin will extend the test_func of any view using
    the UserPassesTestMixin to check the requesting users group membership '''
    allowed_groups = [] #Overwrite, or append, to this with the name of the required django groups
    allow_superusers = True #If true then a django superuser will be granted access regardless of group membership

    def test_func(self):
        ''' an extended test_func that checks group membership '''
        #First the parent class' test_func must pass
        if super().test_func() == False: return False
        #Next, if allowed groups is an empty list it is taken to be permissive
        if self.allowed_groups == []: return True
        #Now begin the test to see if this user can proceed
        #Test 1: Is the user a super user? (If allowed)
        if self.allow_superusers and self.request.user.is_superuser:
            return True
        #Test 2: Does the user belong to an allowed group?
        user_groups = self.request.user.groups.all().values_list('name',flat=True)
        intersect = set(user_groups).intersection(self.allowed_groups)
        if len(intersect) > 0:
            return True
        return False

class SinglePlotMixin:
    ''' This mixin creates a potly figure based on a FilterView that is using
    the PlotSettingsFilterMixin '''
    plot_width = 1000
    max_records = 1_000_000_000

    def get_fig(self):
        self.plot_df = DF()
        if self.object_list.count() > self.max_records:
            emsg = f'Number of records must be < {self.max_records} to produce plot.  Please filter more'
            messages.warning(self.request, emsg)
            return

        ### Get Plot Settings ###
        x = self.request.GET.get('x')
        y = self.request.GET.get('y')

        color = self.request.GET.get('color')
        plot_type = self.request.GET.get('plot_type')
        agg_by = self.request.GET.get('aggregate_by')
        N_min = self.request.GET.get('N_min')
        if x == None:
            return None
        if N_min in [None, '']:
            N_min = 0
        N_min = int(N_min)

        ############################
        qs = self.object_list
        qs = qs.annotate(dtg_=F(self.dtg_str))

        keep_vals = ['dtg_']
        if x not in ['day', 'week', 'month', 'quarter', 'year']:
            keep_vals.append(x)
        if agg_by not in ['day', 'week', 'month', 'quarter', 'year'] and agg_by != None:
            keep_vals.append(agg_by)

        yd = self.Y_CONFIG.get(y)
        for val in yd.get('val_list'):
            keep_vals.append(val)

        ### Get x and y verbose
        y_verbose = yd.get('verbose')
        if y_verbose == None:
            y_verbose = y
        x_verbose = dict(self.choices.get('X_CHOICES')).get(x)
        if x_verbose == None:
            x_verbose = x

        if color and color not in keep_vals:
            keep_vals.append(color)
        df = read_frame(qs.values(*keep_vals))
        if df.empty:
            self.plot_df = df
            return
        df.dtg_ = to_datetime(df.dtg_)

        period_dict = {
            'day': {'pcode': 'd', 'date_format': "%Y-%m-%d"},
            'week': {'pcode': 'W', 'date_format': "%Y-W%U"},
            'month': {'pcode': 'M', 'date_format': "%Y-%m"},
            'quarter': {'pcode': 'Q', 'date_format': "%Y-Q%q"},
            'year': {'pcode': 'Y', 'date_format': "%Y"},
        }
        date_format = None
        pcode = None
        for key, d in period_dict.items():
            if agg_by == key or x == key:
                df[key] = df['dtg_'].dt.to_period(
                    d.get('pcode')).dt.to_timestamp()
                if x == key:
                    pcode = d.get('pcode')
                    date_format = d.get('date_format')

        groupby = [agg_by]
        if x != agg_by:
            groupby.append(x)
        if color and color not in agg_by:
            groupby.append(color)

        odf = df.groupby(groupby).apply(
            yd.get('func')).reset_index().rename(columns={0: y})
        ndf = df.groupby(groupby).count().reset_index()
        odf['N'] = ndf.iloc[:, -1]
        ### Filter Data Frame to Only include sample size > N_min
        odf = odf[odf['N'] >= N_min]
        # If filtering makes empty DF set plot_df and return None
        if odf.empty:
            self.plot_df = odf
            return
        ####
        args = [odf]
        kwargs = dict(x=x, y=y, width=self.plot_width)
        if color:
            kwargs['color'] = color
        if 'bar' in plot_type:
            if plot_type.endswith('g'):
                kwargs['barmode'] = 'group'
            plot_obj = px.bar
        if plot_type == 'box':
            plot_obj = px.box
        if plot_type == 'line':
            plot_obj = px.line
        if plot_type == 'violin':
            kwargs['points'] = 'all'
            kwargs['box'] = True
            plot_obj = px.violin
        if plot_type == 'scatter':
            plot_obj = px.scatter

        odf = odf.reset_index(drop=True)
        self.plot_df = odf
        fig = plot_obj(*args, **kwargs)

        if date_format:
            todf = odf.copy()
            if len(todf) > 15:
                c = round(len(todf)/15, -1)
                todf = todf[(todf.index % c == 0) | (
                    todf.index == todf.index.max())]
            tvals = todf[x]
            fig.update_xaxes(
                tickvals=tvals,
                tickformat=date_format,
            )
        fig.update_layout(
            xaxis_title=x_verbose, yaxis_title=y_verbose
        )
        return offline.plot(fig, auto_open=False, output_type="div")

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        choices = dict(
            X_CHOICES=[('year', 'Year'), ('quarter', 'Quarter'),
                       ('month', 'Month'), ('week', 'Week'), ('day', 'Day'), ],
            Y_CHOICES=[],
            COLOR_CHOICES=[(None, '--------')],
            PLOT_TYPE_CHOICES=(
                ('barg', 'Bar-Grouped'), ('bars', 'Bar-Stacked'),
                ('line', 'Line'), ('scatter', 'Scatter'),
                ('box', 'Box'), ('violin', 'Violin'),
            ),
            AGG_CHOICES=[
                ('quarter', 'Quarter'), ('month',
                                         'Month'), ('week', 'Week'), ('day', 'Day')
            ]
        )

        for key, yd in self.Y_CONFIG.items():
            choices.get('Y_CHOICES').append((key, yd.get('verbose')))

        if hasattr(self, 'X_CHOICES'):
            choices['X_CHOICES'] = self.X_CHOICES

        if hasattr(self, 'X_CHOICES_EXTRA'):
            for tup in self.X_CHOICES_EXTRA:
                choices.get('X_CHOICES').append(tup)

        if hasattr(self, 'COLOR_CHOICES'):
            choices['COLOR_CHOICES'] = self.COLOR_CHOICES

        if hasattr(self, 'COLOR_CHOICES_EXTRA'):
            for tup in self.COLOR_CHOICES_EXTRA:
                choices.get('COLOR_CHOICES').append(tup)

        if hasattr(self, 'AGG_CHOICES'):
            choices['AGG_CHOICES'] = self.AGG_CHOICES

        if hasattr(self, 'AGG_CHOICES_EXTRA'):
            for tup in self.AGG_CHOICES_EXTRA:
                choices.get('AGG_CHOICES').append(tup)

        self.choices = choices
        kwargs['choices'] = choices

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fig'] = self.get_fig()
        context['plot_df'] = self.plot_df
        return context

