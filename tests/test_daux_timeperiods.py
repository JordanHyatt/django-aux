from django.test import TestCase
from django_aux_timeperiods.models import *
import pandas as pd
import datetime as dt
import itertools

#------------TIME PERIOD TESTS------------
class CommonTimePeriodSetup(TestCase):
    ''' Basic setup that runs prior to each Test '''
    
    def setUp(self):
        self.models = [Year, Month, Week, Day]

class TestTimePeriodBase(CommonTimePeriodSetup):
    ''' A Test Class for the TimePeriodBase model '''

    def test_period(self):
        ''' test TimePeriods period property method '''
        #I'm not sure how to test this without just re-running the exact same logic in the method itself.
        #This is import though as all the other tests seem to be using this property method
        today = dt.datetime.now().date()
        testday = dt.datetime(1988,8,28).date() #A great day in History
        for date in [today, testday, dt.datetime(2099,12,31)]:
            day = Day(date=date)
            day.save()
            year,_ = Year.objects.get_or_create(year_num=date.year)
            month,_ = Month.objects.get_or_create(year_num=date.year,month_num=date.month)
            week,_ = Week.objects.get_or_create(year_num=date.year,week_num=date.isocalendar()[1])
            self.assertEqual(pd.Period(date, freq='D'), day.period)            
            self.assertEqual(pd.Period(date, freq='W'), week.period)
            self.assertEqual(pd.Period(year=date.year, freq='Y'), year.period)
            self.assertEqual(pd.Period(year=date.year, month=date.month, freq='M'), month.period)

    def test_get_or_create_n_from_current(self):
        ''' test TimePeriods get_or_create_n_from_current method '''
        now = dt.datetime.now()
        def get_target_period(n, freq):
            now = dt.datetime.now()
            if n == 0:
                return pd.Period(now, freq=freq)
            if n < 0:
                pr = pd.period_range(end = now, periods=abs(n)+1, freq=freq)
                return pr[0]
            else:
                pr = pd.period_range(start = now, periods=abs(n)+1, freq=freq)
                return pr[-1]     

        ns = list(range(-13,15))
        models = [Year, Month, Week, Day]
        for n, model in itertools.product(ns, models):
            obj,_ = model.get_or_create_n_from_current(n=n)
            freq = model.freq_map.get(model.__name__)
            target = get_target_period(n, freq)
            self.assertEqual(obj.period, target)


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
        for cls in self.models:            
            self.assertEqual(
                pd.Period.now(cls.freq_map[cls.__name__]),
                cls.get_or_create_current_period()[0].period
            )

    def test_get_rel_status(self):
        ''' Test Timeperiods get_rel_status method '''    
        now = dt.datetime.now()
        past = now - dt.timedelta(days=366)
        future = now + dt.timedelta(days=366)
        for cls in self.models:
            current,_ = cls.get_or_create_current_period()
            self.assertEqual(current.get_rel_status(), 'present')
            self.assertEqual(current.get_rel_status(dtg=future), 'past')
            self.assertEqual(current.get_rel_status(dtg=past), 'future')

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
