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

    def _pre_setup(self):
        # Django reconstruye self.client justo aquí, en cada test, SIEMPRE —
        # a diferencia de setUp(), esto no depende de que las subclases
        # llamen a super().setUp(). Autenticar en este hook hace que sea
        # imposible saltarse la autenticación por un setUp() mal escrito.
        super()._pre_setup()
        self.client.force_authenticate(user=self.user)
