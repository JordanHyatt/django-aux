from django.test import TestCase, RequestFactory, Client
from django_aux.models import *
from .models import Person
from .views import PersonLookup
from django.contrib.auth.models import User

#------------Django-Aux TESTS------------


class TestSaveFilterMixin(TestCase):
    ''' Test Case for SaveFilterMixin '''

    def setUp(self):
        # create a request factory that all tests have access to
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user('billy', password = 'password')
        self.client.login(username='billy', password='password')
        

    def test_savefiltermixin(self):
        ''' Test functionality of save filter mixin '''
        response = self.client.get('/person-lookup')
        self.assertIsNone(response.wsgi_request.session.get('PersonLookup_qstr'))
        response = self.client.get('/person-lookup', {'last_name__icontains': 'hyatt', 'first_name__icontains':'jordan'})
        qstr = response.wsgi_request.session.get('PersonLookup_qstr')
        self.assertEqual(qstr, 'last_name__icontains=hyatt&first_name__icontains=jordan')
        response = self.client.get('/person-lookup')
        qstr = response.wsgi_request.session.get('PersonLookup_qstr')
        self.assertEqual(qstr, 'last_name__icontains=hyatt&first_name__icontains=jordan')
        response = self.client.get('/person-lookup', {'clear_filter': 'Clear Filter'})
        qstr = response.wsgi_request.session.get('PersonLookup_qstr')
        print(qstr, 'BLAHHH')