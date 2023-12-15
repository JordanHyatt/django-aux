import pandas as pd
from pandas import DataFrame as DF

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Country(models.Model):
    ''' A instance of this class represents a country in the world using the ISO 3166-1 standard '''
    id = models.BigAutoField(primary_key=True)
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
    id = models.BigAutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT)
    iso_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=50)

    
    @staticmethod
    def clean_df(df, country):
        MANUAL_CATEGORY = {
            'AF':'Province'
        }
        if 'Code' not in df.columns:
            return DF()
        rtups = [('Code','code')]
        for col in df.columns:
            if 'subdivision name (en)' in col.lower():
                rtups.append((col, 'name'))
            if 'subdivision category' in col.lower():
                rtups.append((col, 'category'))
        keep_cols = dict(rtups).values()
        for rtup in rtups:
            df.columns = df.columns.str.replace(*rtup, regex=False)      
        df = df.copy()[keep_cols]
        if 'name' not in df.columns:
            df['name'] = 'N/A'
        if 'category' not in df.columns:
            df['category'] = MANUAL_CATEGORY.get(country.alpha2, 'subdivision')
        return df


    @classmethod
    def get_create_df(cls, country):
        """ method retreives the data needed to create objects from wikipedia """
        url = f'https://en.wikipedia.org/wiki/ISO_3166-2:{country.alpha2}'
        dfs = pd.read_html(url)
        df = DF()
        for tdf in dfs:
            tdf = cls.clean_df(tdf, country)
            if tdf.empty: continue
            df = pd.concat([df, tdf])
        df.drop_duplicates('code', keep='first', inplace=True)
        return df


    @classmethod
    def create_objs_from_country(cls, country):
        ''' Method takes a coutnry object and creates all Subdivisions for that country '''
        df = cls.get_create_df(country)
        if df.empty: 
            return
        for tup in df.itertuples():
            cls.objects.get_or_create(
                iso_code = tup.code,
                defaults = dict(
                    name = tup.name, category = tup.category, country=country
                )
            )

    def __str__(self):
        return f'{self.iso_code} | {self.name}'


class Coordinate(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['latitude', 'longitude'], name='unique_coord')
        ]


class Address(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    attn = models.CharField(max_length=255, null=True, blank=True)
    street1 = models.CharField(max_length=510, null=True, blank=True)
    street2 = models.CharField(max_length=510, null=True, blank=True)
    street3 = models.CharField(max_length=510, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    subdivision = models.ForeignKey('django_aux_geo.Subdivision', on_delete=models.PROTECT, null=True, blank=True)
    postal_code = models.CharField(max_length=15, null=True, blank=True)
    country = models.ForeignKey('django_aux_geo.Country', on_delete=models.PROTECT, null=True, blank=True)
    coordinate = models.ForeignKey('django_aux_geo.Coordinate', on_delete=models.SET_NULL, null=True, blank=True)

    # Allow for generic FK realtionships to Address
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    fk_object = GenericForeignKey("content_type", "object_id")


    def __str__(self):
        return f'''
        Name: {self.name}
        ATTN: {self.attn}
        Street1: {self.street1}
        Street2: {self.street2}
        Street3: {self.street3}
        City: {self.city}
        Subdivision: {self.subdivision}
        Postal Code: {self.postal_code}
        Country: {self.country}
        '''