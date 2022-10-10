
from django.db import models
import pandas as pd
from pandas import DataFrame as DF



class Country(models.Model):
    ''' A instance of this class represents a country in the world using the ISO 3166-1 standard '''
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

    def __str__(self):
        return f'{self.alpha3}'


class Subdivision(models.Model):
    ''' Represents a country dub division using the ISO 3166-2 standard '''
    country = models.ForeignKey('Country', on_delete=models.PROTECT)
    iso_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=50)


    @classmethod
    def create_objs_from_country(cls, country):
        ''' Method takes a coutnry object and creates all Subdivisions for that country '''
        url = f'https://en.wikipedia.org/wiki/ISO_3166-2:{country.alpha2}'
        dfs = pd.read_html(url)
        df = DF()
        for tdf in dfs:
            if 'Code' in tdf.columns and 'Subdivision category' in tdf.columns: 
                df = tdf
                break 
        if df.empty: return
        df.columns = ['code', 'name', 'category']
        for tup in df.itertuples():
            SubDivision.objects.get_or_create(
                iso_code = tup.code,
                defaults = dict(
                    name = tup.name, category = tup.category, country=country
                )
            )

    def __str__(self):
        return f'{self.iso_code} | {self.name}'