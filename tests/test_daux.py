from django.test import TestCase, RequestFactory, Client
from django_aux.models import *
from django_aux.views import *
from django_aux.utils import PasswordUtils
from .models import Person
from .views import PersonLookup
from .filters import PersonFilter
from django.contrib.auth.models import User

#------------Django-Aux TESTS------------

class TestPasswordUtils(TestCase):
    ''' Test Case for PasswordUtils '''

    def test_check_password(self):
        raise_tests = [
            dict(password='<10', min_length=10, must_have_symbol=False, must_have_caps=False, must_have_digit=False),
            dict(password='password', min_length=1, must_have_symbol=True, must_have_caps=False, must_have_digit=False),
            dict(password='password', min_length=1, must_have_symbol=False, must_have_caps=True, must_have_digit=False),
            dict(password='password', min_length=1, must_have_symbol=False, must_have_caps=False, must_have_digit=True),
        ]
        for test in raise_tests:
            self.assertRaises(AssertionError, PasswordUtils().check_password, test)

        ok_tests = [
            dict(password='password', min_length=1, must_have_symbol=False, must_have_caps=False, must_have_digit=False),
            dict(password='password!', min_length=1, must_have_symbol=True, must_have_caps=False, must_have_digit=False),
            dict(password='passworD', min_length=1, must_have_symbol=False, must_have_caps=True, must_have_digit=False),
            dict(password='password1', min_length=1, must_have_symbol=False, must_have_caps=False, must_have_digit=True),
        ]
        for test in ok_tests:
            # Just make sure there are no raises
            PasswordUtils().check_password(**test)

    def test_generate_password(self):
        for i in range(5,50, 5):
            pw = PasswordUtils().generate_password(N=i)
            # Ensure Length is correct
            self.assertEqual(len(pw), i)
            # Ensure no amgigous characters
            self.assertEqual(len(set(pw).intersection(PasswordUtils.AMBIGUOUS_CHARS)), 0)


class TestSaveFilterMixin(TestCase):
    ''' Test Case for SaveFilterMixin '''

    def setUp(self):
        # create a request factory that all tests have access to
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user('billy', password = 'password')
        self.client.login(username='billy', password='password')
        

    def test_savefiltermixin_get(self):
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
    
    def test_clear_filter(self):
        request = self.factory.get('/person-lookup', {'last_name__icontains': 'hyatt', 'first_name__icontains':'jordan'})
        request.user = self.user
        view = PersonLookup()
        view.setup(request)
        kwargs = view.get_filterset_kwargs(PersonFilter)
        self.assertNotEqual(kwargs, {})
        request = self.factory.get('/person-lookup', {'last_name__icontains': 'hyatt', 'clear_filter': 'Clear Filter'})
        request.user = self.user
        view = PersonLookup()
        view.setup(request)
        kwargs = view.get_filterset_kwargs(PersonFilter)
        self.assertEqual(kwargs, {})

class TestRedirectPrevMixin(TestCase):
    '''A test for the RedirectPrevMixin view mixin '''

    def test_form_takes_request_arg(self):
        ''' Test the form_takes_request_arg property method '''
        #Create a form without request
        class DummyFormNoReq:
            def __init__(self):
                pass
        #Create a view whose form_class can point to our test forms
        class DummyView(RedirectPrevMixin):
            form_class = DummyFormNoReq
        view = DummyView()
        #The form does NOT have request in its (or its parents) constructors
        self.assertFalse(view.form_takes_request_arg)
        #This should not be affected by class inheritance
        class ChildNoReq(DummyFormNoReq):
            pass
        DummyView.form_class = ChildNoReq
        view = DummyView()
        self.assertFalse(view.form_takes_request_arg)
        #Try with request in an init
        class DummyFormReq:
            def __init__(self, request):
                pass
        DummyView.form_class = DummyFormReq
        view = DummyView()
        self.assertTrue(view.form_takes_request_arg)
        #And with inheritance
        class ChildWithReq(DummyFormReq):
                pass
        DummyView.form_class = ChildWithReq
        view = DummyView()
        self.assertTrue(view.form_takes_request_arg)

    #def test_get_form_kwargs(self):
    #   ''' Test the get_forms_kwargs method of a view using RedirectPrevMixin '''
        