from django.urls import reverse
from rest_framework import status

from .base import AuthenticatedAPITestCase


class CORSTestCase(AuthenticatedAPITestCase):
    def test_cors_headers_present_on_get(self):
        response = self.client.get(
            reverse('spatialplan-list'),
            HTTP_ORIGIN='http://localhost:3000',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')

    def test_cors_preflight_options(self):
        response = self.client.options(
            reverse('spatialplan-list'),
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
        self.assertIn('POST', response.headers.get('Access-Control-Allow-Methods', ''))