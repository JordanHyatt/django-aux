
from django.db import models
import datetime as dt
from django.db.models import UniqueConstraint
import pandas as pd


class Year(models.Model):
    ''' An instance of this model represents a year in the Gregorian Calendar.
        Instances should be initialized with year_num.  Save method 
        will derive the other attributes
    '''
    date = models.DateField()
    year_num = models.PositiveSmallIntegerField(unique=True)
    is_leap_year = models.BooleanField()

    @classmethod
    def get_or_create_from_date(cls, date):
        ''' Classmethod will get or create a year object based on the passed date '''
        sdtg = pd.Period(date, freq='Y').start_time
        return cls.objects.get_or_create(year_num=sdtg.year)

    @property
    def period(self):
        ''' property returns a pandas period object representing this instance '''
        return pd.Period(year=self.year_num, freq='Y')

    def set_date(self):
        ''' Method to set the date attribute '''
        self.date = dt.date(self.year_num, 1, 1)

    def set_leap_year(self):
        ''' Method to set the leap_year boolean '''
        self.is_leap_year = self.period.is_leap_year

    def save(self, *args, **kwargs):
        self.set_date()
        self.set_leap_year()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.period)



class Month(models.Model):
    ''' An instance of this model represents a month in the Gregorian Calendar.
        Instances should be initialized with year_num and month_num.  Save method 
        will derive the other attributes
    '''
    NAME_CHOICES = (
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'),
        ('August', 'August'), ('September', 'September'), ('October', 'October'),
        ('November', 'November'), ('December', 'December'))
    ABBR_CHOICES = (
        ('Jan', 'Jan'),('Feb', 'Feb'),('Mar', 'Mar'),('Apr', 'Apr'),('May', 'May'),
        ('Jun', 'Jun'),('Jul', 'Jul'),('Aug', 'Aug'),('Sep', 'Sep'),('Oct', 'Oct'),
        ('Nov', 'Nov'),('Dec', 'Dec')
    )
    MONTH_NUM_CHOICES = [(i,str(i)) for i in range(1,13)]
    date = models.DateField()
    year = models.ForeignKey('Year', on_delete=models.SET_NULL, null=True)
    year_num = models.PositiveSmallIntegerField()
    month_num = models.PositiveSmallIntegerField(choices=MONTH_NUM_CHOICES)
    name = models.CharField(max_length=10, choices=NAME_CHOICES)
    abbr = models.CharField(max_length=10, choices=NAME_CHOICES)

    class Meta:
        constraints = [UniqueConstraint(fields=['year_num', 'month_num'], name='unique_month')]

    @classmethod
    def get_or_create_from_date(cls, date):
        ''' Classmethod will get or create a month object based on the passed date '''
        sdtg = pd.Period(date, freq='M').start_time
        return cls.objects.get_or_create(year_num=sdtg.year, month_num=sdtg.month)

    @property
    def period(self):
        ''' property returns a pandas period object representing this instance '''
        return pd.Period(year=self.year_num, month=self.month_num, freq='M')

    def set_date(self):
        ''' Method to derive the date attribute '''
        self.date = dt.date(self.year_num, self.month_num, 1)

    def set_name(self):
        ''' Method sets the name attribute '''
        self.name = self.NAME_CHOICES[self.month_num-1][0]

    def set_abbr(self):
        ''' Method sets the abbr attribute '''
        self.name = self.ABBR_CHOICES[self.month_num-1][0]      

    def set_year(self):
        ''' Method sets the year FK attribute. Creates the instance if necessary '''
        self.year, _ = Year.objects.get_or_create(year_num=self.year_num)

    def save(self, *args, **kwargs):
        self.set_date()
        self.set_name()
        self.set_abbr()
        self.set_year()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.period)

class Week(models.Model):
    ''' An instance of this model represents a week in the Gregorian Calendar.
        Numbering convention follows ISO 8601. Weeks always start on Monday and 
        week 1 of the year is the first week this the majority of its 7 days in January.
        Instances should be initialized with year_num and week_num.  Save method 
        will derive the other attributes
    '''
    WEEK_NUM_CHOICES = [(i,str(i)) for i in range(1,53)]
    date = models.DateField()
    year_num = models.PositiveSmallIntegerField()
    week_num = models.PositiveSmallIntegerField(choices=WEEK_NUM_CHOICES)

    class Meta:
        constraints = [UniqueConstraint(fields=['year_num', 'week_num'], name='unique_week')]

    @classmethod
    def get_or_create_from_date(cls, date):
        ''' Classmethod will get or create a week object based on the passed date '''
        sdtg = pd.Period(date, freq='W').start_time
        return cls.objects.get_or_create(year_num=sdtg.year, week_num=sdtg.week)

    @property
    def end_dates(self):
        ''' property returns a list of week end dates for the year of this instance '''
        start = pd.to_datetime(dt.date(self.year_num,1,1)).to_period('W').start_time
        end = pd.to_datetime(dt.date(self.year_num,12,31)).to_period('W').end_time
        dates = pd.date_range(start, end, freq='W')
        if start.week != 1:
            dates = dates[1:]
        if end.week < 52:
            dates = dates[:-1]
        return dates

    @property
    def period(self):
        ''' property returns a pandas period object representing this instance '''
        edate = self.end_dates[self.week_num-1]
        return pd.Period(edate, freq='W')

    def set_date(self):
        ''' Method to derive the date attribute '''
        self.date = self.period.start_time.date()

    def set_year(self):
        ''' Method sets the year FK attribute. Creates the instance if necessary '''
        self.year, _ = Year.objects.get_or_create(year_num=self.year_num)

    def save(self, *args, **kwargs):
        self.set_date()
        self.set_year()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.period)


class Day(models.Model):
    ''' An instance of this model represents a day in the Gregorian Calendar.
        Instances should be initialized with a date.  Save method 
        will derive the other attributes
    '''
    month = models.ForeignKey('Month', on_delete=models.SET_NULL, null=True)
    week = models.ForeignKey('Week', on_delete=models.SET_NULL, null=True)
    date = models.DateField(unique=True)

    @property
    def period(self):
        ''' property returns a pandas period object representing this instance '''
        return pd.Period(self.date, freq='D')

    def set_month(self):
        ''' Method sets the year FK attribute. Creates the instance if necessary '''
        self.month, _ = Month.objects.get_or_create(year_num=self.date.year, month_num=self.date.month)

    def set_week(self):
        ''' Method sets the week FK attribute. Creates the instance if necessary '''
        self.week, _ = Week.get_or_create_from_date(self.date)

    def save(self, *args, **kwargs):
        self.set_month()
        self.set_week()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.period)