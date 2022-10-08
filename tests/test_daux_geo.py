from django.test import TestCase
from django_aux_geo.models import *

#------------GEO TESTS------------




class TestCountry(TestCase):
    ''' TestCase for the Country model '''

    def test_create_objs(self):
        Country.create_objs()
        for alpha2 in ['AD','CA','FR','US']:
            self.assertTrue(Country.objects.filter(alpha2=alpha2).exists())