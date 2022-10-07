from django_tables2 import SingleTableMixin
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Q
from pandas import isna, DataFrame as DF, to_datetime
import inspect
from django.contrib import messages
from django.db.models import F, Count
from django_filters.views import FilterView
from django_pandas.io import read_frame
from django.contrib.auth.mixins import UserPassesTestMixin
import plotly.express as px
from plotly import offline

class SaveFilterMixinNT:
    """ This Mixin Can be used to save
    the users filter selections after navegating away from the lookup page"""

    def get(self, request, *args, **kwargs):
        view_name = self.__class__.__name__
        qstr = request.GET.urlencode()
        full_path = request.get_full_path()
        if qstr != '':
            self.request.session[f'{view_name}_qstr'] = qstr
            return super().get(request)
        else:
            qstr = request.session.get(f'{view_name}_qstr')
            if qstr != None:
                fp = full_path + '?' + qstr
            else:
                fp = full_path
            if isna(qstr) or '_export' in fp:
                return super().get(request, *args, **kwargs)
            else:
                return redirect(fp)

    def get_filterset_kwargs(self, *args):
        kwargs = super().get_filterset_kwargs(*args)
        if 'clear_filter' in self.request.GET.keys():
            return {}
        else:
            return kwargs

class SaveFilterMixin(SingleTableMixin, SaveFilterMixinNT):
    ''' SaveFilterMixin Classic (for use with SingleTableMixin) '''

class InlineFormsetMixin:
    ''' This mixin allows for multiple formset factories to be injected and processed in a form view '''
    factories = [] # list of dictionaries that must contain the key factory and the value of a formset factory instance, helper and herder are optional
    form_helper = None
    template_name = 'django_aux/inline-formset.html'
    addlines_url = None # set this in the view to have the addlines btn redirect here with self.object.pk as an arg
    
    def get_context_data(self, *args, factories=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if factories == None:
            factories = [fd.copy() for fd in self.factories]
            for fd in factories:
                if self.request.POST:
                    fd['factory'] = fd['factory'](self.request.POST, instance=self.object)
                else:
                    fd['factory'] = fd['factory'](instance=self.object)
        context['factories'] = factories
        context['form_helper']=self.form_helper if self.form_helper else None
        return context
            
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None
        context = self.get_context_data()
        form = self.get_form()
        if not form.is_valid():
            print(form.errors)
            return self.form_invalid(form)
        fdsv = True
        for fd in context['factories']:
            if not fd['factory'].is_valid():
                print(fd['factory'].errors)
                fdsv = False
        if fdsv and form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form=form, factories=context['factories'])

    def form_valid(self, form):
        self.object = form.save()
        context = self.get_context_data()
        for fd in context['factories']:
            if fd['factory'].is_valid():
                fd['factory'].save()
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form, factories):
        return self.render_to_response(self.get_context_data(form=form, factories=factories))

    def get_success_url(self):
        if 'addlines' in self.request.POST and self.addlines_url:
            #user defined a redirect url for the addlines btn, default behavior sends pk as arg
            return reverse_lazy(self.addlines_url, kwargs={'pk':self.object.pk})
        elif 'addlines' in self.request.POST and not self.addlines_url:
            #adding lines to form but no redirect url given. Use default behavior
            return self.request.path_info
        else:
            #add lines was not clicked, use default success_url
            return super().get_success_url()

class DashFilterView(FilterView):
    ''' A view for passing filter qs to a dash app '''
    plotly_app_name = None #set this for dash functionality
    template_name = 'django_aux/dash-filter.html'
    values_args = []    #passing all sorts of args and kwargs for backend qs
    values_kwargs = {}
    annotate_kwargs = {}
    filter_args = []
    filter_kwargs = {}
    to_json_kwargs = dict(date_format='iso', orient='records')

    def get_context_data(self, *args, **kwargs):   
        context = super().get_context_data(*args, **kwargs)
        context['plotly_app_name'] = self.plotly_app_name
        context['style_str'] = "min-width:1500px"        
        context['initial_arguments'] = self.get_initial_arguments()
        return context
        
    def get_initial_arguments(self):
        qs = self.object_list.filter(
            *self.filter_args, **self.filter_kwargs
        ).annotate(
            **self.annotate_kwargs
        ).values(
            *self.values_args, **self.values_kwargs
        )
        df = read_frame(qs).astype(str)
        data = df.to_json(**self.to_json_kwargs)
        return {'data':{'children':data}}

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
        if next: 
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
        ''' an overwritten UserPassesTest test_func that checks group membership '''
        #if allowed groups is an empty list it is taken to be permissive
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


class PlotlyMixin:
    ''' This mixin generates a dynamic plotly plot, must be used with a filter that inherits PlotSettingsFilterMixin '''
    plot_width = 1000
    plot_height = None
    max_records = 1_000_000_000


    def check_qs_count(self):
        """ Performs a check to see if the queryset count is greater than the max allowed records

        Returns:
            bool: Indicting whether or the qs was too large
        """        
        if self.object_list.count() > self.max_records:
            emsg = f'Number of records must be < {self.max_records} to produce plot.  Please filter more'
            messages.warning(self.request, emsg)
            return False
        return True   


    @staticmethod
    def add_values(value, vargs, vkwargs):
        """Static method that takes a "value" determines its type and add it to vargs or vkwargs appropriately
        Args:
            value (Any): either a argument or keyword argument to be passed to the Queryset values method
            vargs (list): list of arguments to be passed to Queryset values method
            vkwargs (dict): dict of keyword arguments to be passed to Queryset values method

        """        
        if type(value) == dict:
            vkwargs.update(value)
        else:
            vargs.append(value)

    def get_plot_settings(self):
        """ Method pulls users plot settings from the get request and stores them as instance attributes """ 
        attrs = ['x','y','color','plot_type','aggregate_by','N_min','y_min','y_max']
        for attr in attrs:
            val = self.request.GET.get(attr)
            if val == '': val=None
            setattr(self,attr,val)
        if self.N_min in [None, '']:
            self.N_min = 0
        self.N_min = int(self.N_min)
        ### Get x and y verbose
        self.yd = self.Y_CONFIG.get(self.y)
        self.y_verbose = self.yd.get('verbose') if self.yd else ''
        if self.y_verbose == None:
            self.y_verbose = self.y
        self.x_verbose = dict(self.choices.get('X_CHOICES')).get(self.x)
        if self.x_verbose == None:
            self.x_verbose = self.x

    def get_vargs_vkwargs(self):
        """Method estabishes and returns args and kwargs to be passed to the
            Queryset values method

        Returns:
            tuple: Tuple containing vargs and vkwargs
        """          
        vargs = []
        vkwargs = {} 
        for label in [self.x, self.color, self.aggregate_by]:
            if label == None:
                continue
            val = self.CHOICE_VALUES_MAP.get(label)
            self.add_values(val, vargs, vkwargs) 
        return vargs, vkwargs  

    def get_akwargs(self):
        """Method estabishes and returns the kwargs to be passed to the
            Queryset annotate method

        Returns:
            dict: a dict containing the annotate kwargs
        """          
        agg_func = self.yd.get('agg_expr')
        akwargs = {f'{self.y}':agg_func}
        akwargs['N'] = Count('id')
        return akwargs 

    def get_grouped_qs(self):
        """Method generates and returns the grouped/aggregated queryset to be used in the plot

        Returns:
            Queryset: The grouped queryset to be plotted
        """        
        qs = self.object_list
        vargs, vkwargs = self.get_vargs_vkwargs()
        akwargs = self.get_akwargs()
        fkwargs = {'N__gte':self.N_min}
        if self.y_min: fkwargs[f'{self.y}__gte'] = self.y_min
        if self.y_max: fkwargs[f'{self.y}__lte'] = self.y_max
        fargs = [~Q(**{f'{self.x}':None})]
        if self.color != None: fargs.append(~Q(**{f'{self.color}':None}))
        if self.aggregate_by != None: fargs.append(~Q(**{f'{self.aggregate_by}':None}))
        gqs = qs.values(*vargs, **vkwargs).annotate(**akwargs).filter(*fargs, **fkwargs).order_by(self.x)
        return gqs

    def get_px_args_kwargs_obj(self):
        """Method generates and returns the args, kwargs and plotly.express object to be used in the plot

        Returns:
            tuple: tuple containg the args, kwargs and px object
        """        
        args = [self.plot_df]
        kwargs = dict(x=self.x, y=self.y, width=self.plot_width, height=self.plot_height)
        if self.color:
            kwargs['color'] = self.color
        if 'bar' in self.plot_type:
            if self.plot_type.endswith('g'):
                kwargs['barmode'] = 'group'
            plot_obj = px.bar
        if self.plot_type == 'box':
            plot_obj = px.box
        if self.plot_type == 'line':
            plot_obj = px.line
        if self.plot_type == 'violin':
            kwargs['points'] = 'all'
            kwargs['box'] = True
            plot_obj = px.violin
        if self.plot_type == 'scatter':
            plot_obj = px.scatter
        return args, kwargs, plot_obj

    def get_fig(self):
        """Method generates and returns a plotly Figure object using 
            class variables set in the derived class

        Returns:
            plotly.graph_objects.Figure: A plotly Figure instance
        """    
        self.plot_df = DF()    
        if self.check_qs_count() == False: 
            return
        self.get_plot_settings()
        if self.x == None or self.y == None:
            return None
        gqs = self.get_grouped_qs()
        self.plot_df = read_frame(gqs)
        args, kwargs, plot_obj = self.get_px_args_kwargs_obj()
        fig = plot_obj(*args, **kwargs)
        fig.update_layout(
            xaxis_title=self.x_verbose, yaxis_title=self.y_verbose
        )
        return offline.plot(fig, auto_open=False, output_type="div")


    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        x_choices = self.X_CHOICES
        agg_choices = [(None,'------')]
        color_choices = [(None,'------')]
        if not hasattr(self, 'COLOR_CHOICES'):
            color_choices += self.X_CHOICES
        else:
            color_choices = self.COLOR_CHOICES
        if not hasattr(self, 'AGG_CHOICES'):
            agg_choices += self.X_CHOICES   
        else:
            agg_choices = self.AGG_CHOICES

        y_choices = []
        for key, yd in self.Y_CONFIG.items():
            y_choices.append((key, yd.get('verbose')))  

        choices = dict(
            X_CHOICES=x_choices,
            Y_CHOICES=y_choices,
            COLOR_CHOICES=color_choices,
            PLOT_TYPE_CHOICES=(
                ('barg', 'Bar-Grouped'), ('bars', 'Bar-Stacked'),
                ('line', 'Line'), ('scatter', 'Scatter'),
                ('box', 'Box'), ('violin', 'Violin'),
            ),
            AGG_CHOICES=agg_choices
        )
        self.choices = choices
        kwargs['choices'] = choices
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fig'] = self.get_fig()
        context['plot_df'] = self.plot_df
        return context


class SinglePlotMixin:
    ''' This mixin creates a potly figure based on a FilterView that is using
    the PlotSettingsFilterMixin '''
    plot_width = 1000
    max_records = 1_000_000_000

    def check_qs_count(self):
        if self.object_list.count() > self.max_records:
            emsg = f'Number of records must be < {self.max_records} to produce plot.  Please filter more'
            messages.warning(self.request, emsg)
            return False
        return True       

    def get_fig(self):
        self.plot_df = DF()
        
        if self.check_qs_count() == False:
            return

        ### Get Plot Settings ###
        x = self.request.GET.get('x')
        y = self.request.GET.get('y')
        color = self.request.GET.get('color')
        plot_type = self.request.GET.get('plot_type')
        agg_by = self.request.GET.get('aggregate_by')
        N_min = self.request.GET.get('N_min')
        if x == None or y == None:
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

