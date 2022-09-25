from django.test import TestCase
from django_aux_timeperiods.models import *


class TestTimePeriod(TestCase):
    ''' A test case for TimePeriod Objects '''

    def test_method(self):
        ''' test equips clean_sn method '''
        month,_ = Month.get_or_create_n_from_current(n=1)
        print(month)