from factory.random import randgen
from factory.fuzzy import BaseFuzzyAttribute
from numpy import floor
from datetime import timedelta

class FuzzyTimeDelta(BaseFuzzyAttribute):
    """ A Custom Fuzzyclass for creating random timedelta objects

    Args:
        lower_bound (timedelta, optional): lowerbound for random generation. Defaults to timedelta(0) (zero days).
        upper_bound (timedelta, optional): upperbound for random generation. Defaults to timedelta(1) (one day).
        precision (str, optional): percision of resulting timedelta object. Defaults to 'seconds'
            valid options ['microseconds', 'seconds', 'minutes', 'hours', 'days'].
    """    

    def __init__(self, lower_bound=timedelta(0), upper_bound=timedelta(1), precision='seconds'):     
        super().__init__()
        self.lb = lower_bound
        self.ub = upper_bound
        self.precision = precision

    def fuzz(self):
        """Call this method to generate and return the random timedelta

        Returns:
            timedelta: random timedelta
        """        
        pmap = {
            'microseconds':1,
            'seconds':1*10**6,
            'minutes':1*10**6*60,
            'hours':1*10**6*60*60,
            'days':(1*10**6*60*60*24),
        }
        lmu = int(self.lb.total_seconds()*10**6)
        umu = int(self.ub.total_seconds()*10**6)
        rmu = randgen.randrange(lmu,umu)
        mu = floor(rmu/pmap[self.precision])*pmap[self.precision]
        return timedelta(microseconds=mu)