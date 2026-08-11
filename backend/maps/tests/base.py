from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthenticatedAPITestCase(APITestCase):
    """Base test case that authenticates requests for API integration tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='api-test-user',
            password='test-pass-123',
        )

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
