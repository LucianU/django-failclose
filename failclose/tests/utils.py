from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from failclose import utils
from failclose.tests.urls import ugly

class SafeDecoratorTest(TestCase):
    def setUp(self):
        self.undecorated_view = lambda: None

    def test_undecorated_view(self):
        """Checks that an undecorated view doesn't
        have a 'safe' attribute"""

        self.assertRaises(AttributeError, getattr, self.undecorated_view, 'safe')

    def test_decorated_view(self):
        """Checks that a decorated view has a 'safe' attribute
        set to True and the same name as the original view"""

        decorated_view = utils.safe(self.undecorated_view)

        self.assertTrue(decorated_view.safe)
        self.assertEqual(decorated_view.__name__, self.undecorated_view.__name__)

class GetProjectNameTest(TestCase):
    def setUp(self):
        self.old_project_name = getattr(settings, 'PROJECT_NAME', None)
        settings.PROJECT_NAME = 'foobar'

    def test_project_name(self):
        """Tests the ability to retrieve the project name from
        the PROJECT_NAME setting"""

        self.assertEqual(utils._get_project_name(), 'foobar')

    def test_root_urlconf(self):
        """Tests the ability to retrieve the project name from
        the ROOT_URLCONF"""

        self.old_root_urlconf = settings.ROOT_URLCONF
        settings.PROJECT_NAME = ''
        settings.ROOT_URLCONF = 'foobar.urls'

        self.assertEqual(utils._get_project_name(), 'foobar')

        settings.ROOT_URLCONF = self.old_root_urlconf

    def test_no_project_name(self):
        """Verifies that an error is raised when the project name
        can't be retrieved"""

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
        """Checks that the app name of an app view is
        retrieved correctly"""

        self.app_view = ugly
        self.assertEqual(utils._get_app_name(self.app_view), 'failclose')

    def test_with_global_view(self):
        """Checks that the app name of a global view is
        the project name"""

        self.global_view = lambda: None
        self.global_view.__module__ = 'foobar.views'
        self.assertEqual(utils._get_app_name(self.global_view), 'foobar')

    def test_with_unknown_view(self):
        """Verifies that a view from an unknown app raises an error"""

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
        """Verifies that valid rules don't raise an error"""

        rules = {
            'failclose': ['pretty', 'ugly'],
            'foobar': [],
        }
        self.assertEqual(utils._validate_rules(rules), None)

    def test_with_invalid_rules(self):
        """Verifies that invalid rules raise an error"""

        rules = {
            'shire': ['bow', 'arrow'],
            'failclose': ['pretty', 'ugly'],
        }
        self.assertRaises(ImproperlyConfigured, utils._validate_rules, rules)

    def tearDown(self):
        if self.old_project_name is not None:
            settings.PROJECT_NAME = self.old_project_name

class IsSafeTest(TestCase):
    def setUp(self):
        self.old_permissions_module = getattr(settings, 'PERMISSIONS_MODULE', None)
        settings.PERMISSIONS_MODULE = ''

        self.view = ugly

    def test_with_no_rules(self):
        """Checks that calling 'is_safe' without rules
        raises an error"""

        self.assertRaises(ImproperlyConfigured, utils.is_safe, self.view)

    def test_unsafe_view(self):
        """Checks that an unsafe view is marked as such"""

        self.assertFalse(utils.is_safe(self.view, rules={}))

    def test_decorated_view(self):
        """Checks that a decorated view is marked as safe"""

        self.decorated_view = utils.safe(self.view)
        self.assertTrue(utils.is_safe(self.decorated_view, rules={}))

    def test_view_in_rules(self):
        """Checks that a view marked as safe in rules is
        confirmed safe"""

        rules = {
            'failclose': ['ugly']
        }
        self.assertTrue(utils.is_safe(self.view, rules=rules))

    def test_view_in_whitelisted_app(self):
        """Checks that a view from an app considered safe
        is considered safe itself"""

        rules = {
            'failclose': []
        }
        self.assertTrue(utils.is_safe(self.view, rules=rules))

    def test_view_namespaces(self):
        """Verifies that app namespaces are followed when checking
        view safety in rules"""

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
