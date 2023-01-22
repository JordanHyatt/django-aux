class FakeRequest:
    ''' Very simple Request Simulator that will allow for testing 
    Mixins without a full http cycle '''
    def __init__(self, GET=None, POST=None, META=None, method=None):
        self.GET = GET if GET else {}
        self.POST = POST if POST else {}
        self.META = META if META else {}
        self.method = method
