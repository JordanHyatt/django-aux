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
        now = dt.datetime.now()
        for i in range(-13,15):
            #Test Year class
            year,_ = Year.get_or_create_n_from_current(n=i)
            target = now.year + i
            self.assertEqual(year.period.year,target)
            #Test Month class
            month,_ = Month.get_or_create_n_from_current(n=i)
            target_month = (now.month + i%12)
            if target_month > 12: 
                target_month = target_month-12
            self.assertEqual(
                month.period.month, target_month
            )
            ##The year may have rolled over too during shifting months
            target_year = now.year
            month_delta = now.month + i
            if month_delta > 12: target_year = target_year + 1
            if month_delta < 1: target_year = target_year - 1
            self.assertEqual(
                month.period.year, target_year
            )
            #Test Week class
            week,_ = Week.get_or_create_n_from_current(n=i)
            target = now + dt.timedelta(weeks=i)
            self.assertEqual(
                week.period.week, target.date().isocalendar()[1]
            )
            ##The year may have rolled over too during shifting weeks
            target_year = now.year
            week_delta = now.isocalendar()[1] + i
            if week_delta >= 52: target_year = target_year + 1 #IS this only a .= b/c of this specific year's wk 52?!
            if week_delta < 1: target_year = target_year - 1
            self.assertEqual(
                week.period.year, target_year
            )
            #Test Day class
            day,_ = Day.get_or_create_n_from_current(n=i)
            target = now + dt.timedelta(i)
            self.assertEqual(
                day.period.day, target.date().day
            )
            self.assertEqual(
                day.period.month, target.date().month
            )
            self.assertEqual(
                day.period.year, target.date().year
            )


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

class TestMonth(TestCase):
    ''' A Test Class for the Month model '''

    def test_set_year(self):
        month,_ = Month.get_or_create_current_period()
        self.assertEqual(pd.Period.now('Y'), month.year.period)

class TestWeek(TestCase):
    ''' A Test Class for the Week model '''

    def test_set_year(self):
        week,_ = Week.get_or_create_current_period()
        self.assertEqual(pd.Period.now('Y'), week.year.period)

class TestDay(TestCase):
    ''' A Test Class for the Day model '''

    def test_set_month(self):
        day,_ = Day.get_or_create_current_period()
        self.assertEqual(pd.Period.now('M'), day.month.period)

    def test_set_week(self):
        day,_ = Day.get_or_create_current_period()
        self.assertEqual(pd.Period.now('W'), day.week.period)
