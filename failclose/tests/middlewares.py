from django import http
from django.test import TestCase

from failclose.middlewares import FailCloseMiddleware
from failclose.tests.urls import pretty, ugly

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

