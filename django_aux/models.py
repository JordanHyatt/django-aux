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

class CheckOverlapMixin:
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



class Country(models.Model):
    ''' A instance of this class represents a country in the world '''
    alpha2 = models.CharField(max_length=2, null=True)
    alpha3 = models.CharField(max_length=3, unique=True)
    num = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=250)

    @classmethod
    def create_objs(cls, update=False):
        url = 'https://www.iban.com/country-codes'
        df = pd.read_html(url)[0]
        df.columns = ['name', 'alpha2', 'alpha3', 'num']
        
        for tup in df.itertuples():
            alpha2 = None if pd.isna(tup.alpha2) else tup.alpha2
            goc_method = cls.objects.updated_or_create if update else cls.objects.get_or_create
            goc_method(
                alpha3 = tup.alpha3,
                defaults = dict(
                    alpha2=alpha2, num=tup.num, name=tup.name
                )
            )

