from django.test import TestCase
from django_aux_timeperiods.models import *
import pandas as pd
import datetime as dt

#------------TIME PERIOD TESTS------------
class CommonTimePeriodSetup(TestCase):
    ''' Basic setup that runs prior to each Test '''
    
    def setUp(self):
        self.classes = [Year, Month, Week, Day]

class TestTimePeriodBase(CommonTimePeriodSetup):
    ''' A Test Class for the TimePeriodBase model '''

    def test_get_or_create_n_from_current(self):
        ''' test TimePeriods get_or_create_n_from_current method '''
        for i in range(-2,3):
            month,_ = Month.get_or_create_n_from_current(n=i)
            target = (dt.datetime.now().month + i%12)
            if target > 12: target = target-12
            self.assertEqual(
                month.period.month, target
            ) #JMAN/KEVO Test with other classes?!?!

    def test_get_or_create_from_date(self):
        ''' Test accuracy of the get_or_create_from_date class method '''
        testday = dt.datetime(1988,8,28).date() #A great day in History
        today = dt.datetime.now().date()
        for day in [testday, today]:
            yyyy,_ = Year.get_or_create_from_date(day)
            mm,_ = Month.get_or_create_from_date(day)
            ww,_ = Week.get_or_create_from_date(day)
            dd,_ = Day.get_or_create_from_date(day)
            self.assertEqual(
                yyyy.period, pd.Period(year=day.year, freq='Y')
            )
            self.assertEqual(
                mm.period, pd.Period(year=day.year, month=day.month, freq='M')
            )
            self.assertEqual(
                ww.period, pd.Period(day, freq='W')
            )
            self.assertEqual(
                ww.period.week, day.isocalendar()[1]
            )
            self.assertEqual(
                dd.period, pd.Period(day, freq='D')
            )

    def test_get_or_create_current_period(self):
        ''' Test accuracy of the get_or_create_current_period class method '''
        for cls in self.classes:            
            self.assertEqual(
                pd.Period.now(cls.freq_map[cls.__name__]),
                cls.get_or_create_current_period()[0].period
            )