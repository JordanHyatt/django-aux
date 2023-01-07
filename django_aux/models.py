from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from simple_history.models import HistoricalRecords
import pandas as pd

class ModelBase(models.Model):
    class Meta:
        abstract = True
    history = HistoricalRecords(related_name='log', inherit=True)

    @classmethod
    def get_field_names(cls):
        ''' Return a list of the db field names for objects of this class '''
        return [f.name for f in cls._meta.get_fields()]

class CheckRangeMixin:
    '''
        This model mixin adds cleaning functionality to a model that will ensure the value of a ending attr 
        is greater than the value of a start attr. Default will not let them be equal but can be overwritten
    '''
    start_attr = '' # Name of the attr that starts the range (must be overwritten)
    end_attr = '' # Name of the attr that ends the range (must be overwritten)
    allow_zero_diff = False
    clean_during_save = True

    def check_range(self):
        start = self.cleaned_data.get(f'{self.start_attr}')
        end = self.cleaned_data.get(f'{self.end_attr}')
        if self.allow_zero_diff:
            valid = end >= start
        else:
            valid = end > start        
        if not valid:
            raise ValidationError(f'{self.end_attr} must be larger than {self.start_attr}')

    def clean(self):
        cd = super().clean()
        self.check_range()
        return cd

    def save(self, *args, **kwargs):
        if self.clean_during_save:
            self.clean()
        super().save(*args,**kwargs)

class CheckOverlapMixin(CheckRangeMixin):
    ''' 
        This mixin adds cleaning functionality to a model that will not allow a range overlap defined by two attributes.
        default behavior is to include the boundaries, but can be overwritten
    '''
    start_attr = '' # Name of the attr that starts the range (must be overwritten)
    end_attr = '' # Name of the attr that ends the range (must be overwritten)
    extra_filter_attrs = [] # Additional filter attrs to apply before checking for overlap
    include_end_boundary = True
    include_start_boundary = True
    clean_during_save = True

    def clean(self):
        super().clean()
        self.check_overlap()

    def save(self, *args, **kwargs):
        if self.clean_during_save:
            self.clean()
        super().save(*args,**kwargs)

    def check_overlap(self):
        # Overlapping ranges will always meet BOTH of the following conditions
        # 1.) existing end date is >= new start date
        # 2.) existing start date is <= new end date
        fkwargs= {} # initialize filter kwargs
        #  Get the look ups based on boundary cond settings
        slu = 'lte' if self.include_start_boundary else 'lt'
        elu = 'gte' if self.include_end_boundary else 'gt'
        fkwargs[f'{self.end_attr}__{elu}'] = getattr(self, self.start_attr, None)  # condition 1
        fkwargs[f'{self.start_attr}__{slu}'] = getattr(self, self.end_attr, None)  # condition 2
        for fattr in self.extra_filter_attrs:
            fkwargs[fattr] = getattr(self, fattr, None)
        # Count the number of objects (other than the object itself) that meet both conditions
        try:
            bad_count = self.__class__.objects.filter(
                ~Q(id=self.pk),
            ).filter(**fkwargs).count()
        except Exception as e:
            raise ValidationError('Check overlap failed')
        #No other objects should have met that criteria
        if bad_count > 0:
            msg = f'{self.__class__.__name__} cannot overlap another instance'
            if self.extra_filter_attrs != []:
                msg = msg + f' with the same {self.extra_filter_attrs}'
            raise ValidationError(
                msg
            )

