"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import sys
import types

from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from failclose import utils
from failclose.tests.urls import pretty, ugly
from failclose.middlewares import FailCloseMiddleware

class SafeDecoratorTest(TestCase):
    def setUp(self):
        self.undecorated_view = lambda: None

    def test_undecorated_view(self):
        # the safe attribute doesn't exist yet
        self.assertRaises(AttributeError, getattr, self.undecorated_view, 'safe')

    def test_decorated_view(self):
        # marking the dummy as safe
        decorated_view = utils.safe(self.undecorated_view)

        # the safe attribute should be set to True and function name
        # should be identical to the undecorated function's name
        self.assertTrue(decorated_view.safe)
        self.assertEqual(decorated_view.__name__, self.undecorated_view.__name__)

class GetProjectNameTest(TestCase):
    def setUp(self):
        self.old_project_name = getattr(settings, 'PROJECT_NAME', None)
        settings.PROJECT_NAME = 'foobar'

    def test_project_name(self):
        # testing the ability to retrieve the project name from
        # the PROJECT_NAME setting
        self.assertEqual(utils._get_project_name(), 'foobar')

    def test_root_urlconf(self):
        # testing the ability to retrieve the project name from
        # the ROOT_URLCONF
        self.old_root_urlconf = settings.ROOT_URLCONF
        settings.PROJECT_NAME = ''
        settings.ROOT_URLCONF = 'foobar.urls'

        self.assertEqual(utils._get_project_name(), 'foobar')

        settings.ROOT_URLCONF = self.old_root_urlconf

    def test_no_project_name(self):
        # verifying that an error is raised when the project name
        # can't be retrieved
        settings.PROJECT_NAME = ''
        settings.ROOT_URLCONF = 'foo.bar.urls'
        self.assertRaises(ImproperlyConfigured, utils._get_project_name)

    def tearDown(self):
        if self.old_project_name is not None:
            settings.PROJECT_NAME = self.old_project_name

class GetAppNameTest(TestCase):
    def setUp(self):
        # preparing for the project (global) view check
        self.old_project_name = getattr(settings, 'PROJECT_NAME', None)
        settings.PROJECT_NAME = 'foobar'

    def test_with_app_view(self):
        # setting up the view that comes from an actual app
        from django.contrib.auth.views import login
        self.app_view = login
        self.assertEqual(utils._get_app_name(self.app_view), 'auth')

    def test_with_global_view(self):
        # and the one that is supposedly global
        self.global_view = lambda: None
        self.global_view.__module__ = 'foobar.views'
        self.assertEqual(utils._get_app_name(self.global_view), 'foobar')

    def test_with_unknown_view(self):
        # and the one that is from an unknown app
        self.unknown_view = lambda: None
        self.unknown_view.__module__ = 'mordor.views'
        self.assertRaises(ImproperlyConfigured, utils._get_app_name, self.unknown_view)

    def tearDown(self):
        if self.old_project_name is not None:
            settings.PROJECT_NAME = self.old_project_name

class ValidateRulesTest(TestCase):
    def setUp(self):
        self.old_project_name = getattr(settings, 'PROJECT_NAME', None)
        settings.PROJECT_NAME = 'foobar'

    def test_with_valid_rules(self):
        rules = {
            'sessions': [],
            'auth': ['login', 'logout'],
            'foobar': [],
        }
        self.assertEqual(utils._validate_rules(rules), None)

    def test_with_invalid_rules(self):
        rules = {
            'shire': ['bow', 'arrow'],
            'auth': ['login', 'logout'],
        }
        self.assertRaises(ImproperlyConfigured, utils._validate_rules, rules)

    def tearDown(self):
        if self.old_project_name is not None:
            settings.PROJECT_NAME = self.old_project_name

class IsSafeTest(TestCase):
    def setUp(self):
        self.old_permissions_module = getattr(settings, 'PERMISSIONS_MODULE', None)
        settings.PERMISSIONS_MODULE = ''

        from django.contrib.auth.views import login
        self.view = login

    def test_with_no_rules(self):
        self.assertRaises(ImproperlyConfigured, utils.is_safe, self.view)

    def test_unsafe_view(self):
        self.assertFalse(utils.is_safe(self.view, rules={'sessions': []}))

    def test_decorated_view(self):
        self.decorated_view = utils.safe(self.view)
        self.assertTrue(utils.is_safe(self.decorated_view, rules={'sessions': []}))
        del self.view.safe

    def test_view_in_rules(self):
        rules = {
            'auth': ['login']
        }
        self.assertTrue(utils.is_safe(self.view, rules=rules))

    def test_view_in_whitelisted_app(self):
        rules = {
            'auth': []
        }
        self.assertTrue(utils.is_safe(self.view, rules=rules))

    def test_view_namespaces(self):
        # setting up the project used to check the view
        self.old_project_name = getattr(settings, 'PROJECT_NAME', None)
        settings.PROJECT_NAME = 'foobar'

        rules = {
            'foobar': ['login'],
        }
        self.assertFalse(utils.is_safe(self.view, rules=rules))

        # rolling back the settings
        if self.old_project_name is not None:
            settings.PROJECT_NAME = self.old_project_name

    def tearDown(self):
        if self.old_permissions_module is not None:
            settings.PERMISSIONS_MODULE = self.old_permissions_module

class FailCloseMiddlewareTest(TestCase):
    def setUp(self):
        self.middleware = FailCloseMiddleware()

    def test_safe_view(self):
        """Makes sure that a safe view causes the middleware
        to return a 200 response"""

        request = http.HttpRequest()

        response = self.middleware.process_view(request, pretty, (), {})
        self.assertEqual(response.status_code, 200)

    def test_unsafe_view(self):
        """Makes sure that an unsafe view causes the middleware
        to return a 403 response"""

        request = http.HttpRequest()

        response = self.middleware.process_view(request, ugly, (), {})
        self.assertEqual(response.status_code, 403)

class FailCloseAppTest(TestCase):
    urls = 'failclose.tests.urls'

    def setUp(self):
        self.client = Client()
        self.old_permissions_module = getattr(settings, 'PERMISSIONS_MODULE', None)
        settings.PERMISSIONS_MODULE = 'permissions'
        RULES = {
            'failclose': ['pretty'],
        }
        module = types.ModuleType('permissions')
        setattr(module, 'RULES', RULES)
        sys.modules['permissions'] = module

    def test_safe_view(self):
        path = reverse('failclose.tests.urls.pretty')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

    def test_unsafe_view(self):
        path = reverse('failclose.tests.urls.ugly')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        if self.old_permissions_module is not None:
            settings.PERMISSIONS_MODULE = self.old_permissions_module
        sys.modules.pop('permissions')

