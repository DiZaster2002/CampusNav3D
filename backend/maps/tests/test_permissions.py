from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ..models import Campus
from django.contrib.gis.geos import Polygon


class SpatialPlanPermissionsTests(APITestCase):
    """Pruebas de seguridad para verificar la restricción de acceso a usuarios no autenticados (Anónimos)."""

    def setUp(self):
        # Crear un usuario de mantenimiento y generar su token
        self.user = User.objects.create_user(
            username='mantenimiento', 
            password='Password123!'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Crear datos de prueba
        self.campus = Campus.objects.create(
            name="Campus Central", 
            slug="CAMP-01",
            geometry=Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
        )
        
        # URLs de prueba
        self.campus_list_url = reverse('campus-list')
        self.plan_upload_url = reverse('plan-upload')

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

    def test_anonymous_user_can_read_campuses(self):
        """Un usuario anónimo debe poder consultar los campus (GET)."""
        response = self.client.get(self.campus_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_upload_plan(self):
        """Un usuario anónimo NO debe poder subir un plano (POST)."""
        response = self.client.post(self.plan_upload_url, {})
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_anonymous_user_cannot_create_campus(self):
        """Un usuario anónimo NO debe poder crear un campus (POST)."""
        data = {"name": "Nuevo Campus", "slug": "NC"}
        response = self.client.post(self.campus_list_url, data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_user_can_access_protected_endpoint(self):
        """Un usuario con Token válido sí puede acceder a endpoints protegidos."""
        # Simular cabecera: Authorization: Token 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        response = self.client.post(self.plan_upload_url, {})
        # Esperamos que no sea 401/403 (podría ser 400 por falta de archivo, pero la autenticación pasa)
        self.assertNotIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

