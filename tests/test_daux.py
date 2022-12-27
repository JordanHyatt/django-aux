from django.test import TestCase, RequestFactory, Client
from django_aux.models import *
from django_aux.views import *
from django_aux.utils import PasswordUtils
from .models import Person
from .views import PersonLookup
from .filters import PersonFilter
from django.contrib.auth.models import User
from django.views.generic import *
from django import forms
from django.test.client import RequestFactory
from django.test import Client
from django.urls import path, reverse

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

    def setUp(self):
        #Make access to RequestFactory
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='billy', email='bill@bob.com', password='foobar')
        self.client = Client()
        self.client.login(username='billy', password='foobar')

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

    def test_get_form_kwargs(self):
        ''' Test the get_forms_kwargs method of a view using RedirectPrevMixin '''
        #Create a form that does not have request in its constructor
        class DummyForm(forms.ModelForm):
            def __init__(self):
                pass
        #Create a form that can point to the form_set
        class DummyView(RedirectPrevMixin,FormView):
            form_class = DummyForm
        #Make a request to our DummyView
        request = self.request_factory.get('/foo/bar')   
        view = DummyView(request=request)
        # There should not be request in the kwargs
        self.assertFalse(view.form_takes_request_arg)
        self.assertNotIn('request',view.get_form_kwargs())
        #Repeat with a form that takes request and request should be in the kwargs
        class SecondDummyForm(forms.ModelForm):
            def __init__(self,request):
                pass
        class SecondDummyView(RedirectPrevMixin,FormView):
            form_class = SecondDummyForm    
        view = SecondDummyView(request=request)
        self.assertTrue(view.form_takes_request_arg)
        self.assertIn('request',view.get_form_kwargs())

    def test_get_next_is_exception(self):
        orig_path = '/fake/path'
        class DummyView(RedirectPrevMixin, View):
            success_url = '/foo'
        #Build a request to the view
        request = self.request_factory.post('/foo/bar', HTTP_REFERER=orig_path)
        response = DummyView(request=request)
        #No exceptions have been set, redirect to previous
        next = response.request.META.get('HTTP_REFERER')
        self.assertEqual(next, orig_path)
        self.assertFalse(response.get_next_is_exception(next))
        #Add the origin to the exceptions
        DummyView.redirect_exceptions = ['fake']
        response = DummyView(request=request)
        next = response.request.META.get('HTTP_REFERER')
        self.assertTrue(response.get_next_is_exception(next))

    def test_get_success_url(self):
        orig_path = '/fake/path'
        class ParentView(View):
            def get_success_url(self):
                return self.success_url
        class DummyView(RedirectPrevMixin, ParentView):
            success_url = '/foo'
            def get_success_url(self):
                return self.success_url
        #Try without next set
        request = self.client.get('/foo/bar')
        response = DummyView(request=request)        
        self.assertEqual(
            response.get_success_url(), DummyView.success_url
        )
        #Redo with an HTTP_REFERER for the get
        secondrequest = self.client.get('/other/path', HTTP_REFERER=orig_path)
        secondresponse = DummyView(request=secondrequest)
        #print(secondrequest.session.get('nexxt'))
        self.assertEqual(
            secondresponse.get_success_url(), orig_path
        )

    # def test_get(self):
    #     class DummyView(RedirectPrevMixin, View):
    #         success_url = '/success'
    #     path("fake-path", DummyView.as_view(), name="fake-path")
    #     #Scenario 1 - no HTTP_REFERER, no redirect_exception
    #     response = self.client.get(reverse_lazy('fake-path'))
    #     print(response)

    def test_post(self):
        pass
        