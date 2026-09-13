from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SpatialPlanPermissionsTests(APITestCase):
    """Pruebas de seguridad para verificar la restricción de acceso a usuarios no autenticados (Anónimos)."""

    def test_unauthenticated_cannot_upload_plan(self):
        """Verifica que peticiones no autenticadas a /api/plans/upload/ retornen 401 Unauthorized."""
        url = reverse('plan-upload')
        response = self.client.post(url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_approve_plan(self):
        """Verifica que peticiones no autenticadas a /api/plans//approve/ retornen 401 Unauthorized."""
        url = reverse('plan-approve', kwargs={'pk': 1})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_reject_plan(self):
        """Verifica que peticiones no autenticadas a /api/plans//reject/ retornen 401 Unauthorized."""
        url = reverse('plan-reject', kwargs={'pk': 1})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

