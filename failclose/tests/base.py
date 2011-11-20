"""
Tests for faiclose app as a whole
"""

import sys
import types

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

class FailCloseAppTest(TestCase):
    urls = 'failclose.tests.urls'

    def setUp(self):
        self.old_permissions_module = getattr(settings, 'PERMISSIONS_MODULE', None)
        settings.PERMISSIONS_MODULE = 'permissions'
        RULES = {
            'failclose': ['pretty'],
        }
        module = types.ModuleType('permissions')
        setattr(module, 'RULES', RULES)
        sys.modules['permissions'] = module

    def test_safe_view(self):
        """Confirms that, in the case of a safe view, a 200
        response status code is returned"""

        path = reverse('failclose.tests.urls.pretty')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

    def test_unsafe_view(self):
        """Confirms that, in the case of an unsafe view, a 403
        response status code is returned"""

        path = reverse('failclose.tests.urls.ugly')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        if self.old_permissions_module is not None:
            settings.PERMISSIONS_MODULE = self.old_permissions_module
        sys.modules.pop('permissions')

