import django_tables2 as tables

from .models import Country, Subdivision, Address


class CountryTable(tables.Table):
    class Meta:
        model = Country
        exclude = []

class SubdivisionTable(tables.Table):
    class Meta:
        model = Subdivision
        exclude = []

class AddressTable(tables.Table):
    class Meta:
        model = Address
        exclude = []