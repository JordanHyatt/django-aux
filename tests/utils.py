class FakeRequest:
    ''' Very simple Request Simulator that will allow for testing 
    Mixins without a full http cycle '''
    def __init__(self, GET=None, POST=None, META=None, method=None, path_info=''):
        self.GET = GET if GET else {}
        self.POST = POST if POST else {}
        self.META = META if META else {}
        self.method = method
        self.path_info = path_info


class FakeFormsetFactory:
    def __call__(self, data=None, instance=None):
        self.data = data
        self.instance = instance
        return self