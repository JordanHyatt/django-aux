from django.test import TestCase, RequestFactory, Client
from django_aux.models import *
from django_aux.views import *
from django_aux.utils import PasswordUtils
from .models import Person
from .views import PersonLookup, PersonCreate, PersonCreateWithRequest
from .filters import PersonFilter
from django.contrib.auth.models import User
from django.views.generic import *
from django import forms
from django.test.client import RequestFactory
from django.test import Client
from django.urls import path, reverse
from django.contrib.sessions.middleware import SessionMiddleware
from .utils import *

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
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='billy', email='bill@bob.com', password='foobar')
        self.client = Client()
        self.client.login(username='billy', password='foobar')
        self.middleware = SessionMiddleware(lambda x: None)

    def test_form_takes_request_arg(self):
        ''' Test the form_takes_request_arg property method '''
        self.assertFalse(PersonCreate().form_takes_request_arg)
        self.assertTrue(PersonCreateWithRequest().form_takes_request_arg)


    def test_get_form_kwargs(self):
        ''' Test the get_forms_kwargs method of a view using RedirectPrevMixin '''
        request = self.factory.get('/person-create')
        self.assertNotIn('request', PersonCreate(request=request).get_form_kwargs().keys())
        request = self.factory.get('/person-create-request')
        self.assertIn('request', PersonCreateWithRequest(request=request).get_form_kwargs().keys())


    def test_get_next_is_exception(self):
        request = self.factory.get('/person-create')
        pc = PersonCreate(request=request)
        reverse_name = pc.get_next_is_exception('person-delete')
        self.assertEqual(reverse_name, 'person-lookup')

        request = self.factory.get('/person-create')
        pc = PersonCreate(request=PersonCreateWithRequest)
        reverse_name = pc.get_next_is_exception('this-is-ok')
        self.assertEqual(reverse_name, None)


    def test_next(self):
        response = self.client.get('/person-create', HTTP_REFERER='final-destination')
        self.assertEqual(response.wsgi_request.session.get('next'), 'final-destination')

        response = self.client.get('/person-create', HTTP_REFERER='person-delete')
        self.assertEqual(response.wsgi_request.session.get('next'), '/person-lookup')



class TestInlineFormsetMixin(TestCase):
    
    def test_get_current_extra(self):
        ifm = InlineFormsetMixin()
        ifm.max_extra = 10
        ifm.request = FakeRequest(GET = {'extra':None})
        self.assertEqual(ifm.get_current_extra(), 1)
        ifm.request = FakeRequest(GET = {'extra':1})
        self.assertEqual(ifm.get_current_extra(), 1)
        ifm.request = FakeRequest(GET = {'extra':2})
        self.assertEqual(ifm.get_current_extra(), 2)
        # try one that exceeds max
        ifm.request = FakeRequest(GET = {'extra':11})
        self.assertEqual(ifm.get_current_extra(), 10) 

    def test_add_factories_to_context(self):
        ifm = InlineFormsetMixin()
        ifm.factories = [
            {'factory':FakeFormsetFactory(), 'helper':None, 'header':None},
            {'factory':FakeFormsetFactory(), 'helper':None, 'header':None},
        ]
        ifm.request = FakeRequest(method='GET')
        ifm.object = None
        context = {}
        ifm.add_factories_to_context(context)
        num_factories = len(context.get('factories'))
        self.assertEqual(num_factories, 2)


    def test_set_extra_on_factories(self):
        ifm = InlineFormsetMixin()
        ifm.object = None
        ifm.request = FakeRequest(GET = {'extra':2}, method='GET')
        ifm.factories = [
            {'factory':FakeFormsetFactory(), 'helper':None, 'header':None},
            {'factory':FakeFormsetFactory(), 'helper':None, 'header':None},
        ]
        context = {}
        ifm.add_factories_to_context(context)
        ifm.set_extra_on_factories(context)
        for fd in context.get('factories'):
            self.assertEqual(fd.get('factory').extra, 2)

    def test_add_addlines_url_to_context(self):
        ifm = InlineFormsetMixin()
        tests = (
            {'extra':None, 'target':2},
            {'extra':1, 'target':2},
            {'extra':5, 'target':6},
            {'extra':10, 'target':11},
        )
        for td in tests:
            ifm.request = FakeRequest(GET = {'extra':td.get('extra')})
            context = {}
            ifm.add_addlines_url_to_context(context)
            self.assertEqual(context['addlines_url'], f"?extra={td.get('target')}")


    def test_add_removelines_url_to_context(self):
        ifm = InlineFormsetMixin()
        tests = (
            {'extra':None, 'target':1},
            {'extra':1, 'target':1},
            {'extra':5, 'target':4},
            {'extra':10, 'target':9},
        )
        for td in tests:
            ifm.request = FakeRequest(GET = {'extra':td.get('extra')})
            context = {}
            ifm.add_removelines_url_to_context(context)
            self.assertEqual(context['removelines_url'], f"?extra={td.get('target')}")