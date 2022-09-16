
from django.db import models
import pandas as pd




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
