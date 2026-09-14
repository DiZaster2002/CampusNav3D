import io
from PIL import Image
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.gis.geos import Polygon
from rest_framework import status

from maps.models import SpatialPlan, SpatialPlanStatus, Space, Floor, Building, Campus
from maps.tests.base import AuthenticatedAPITestCase


class SpatialPlanLifecycleIntegrationTestCase(AuthenticatedAPITestCase):
    """Pruebas de integración End-to-End para el ciclo de vida completo de un SpatialPlan."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        poly = Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0)))

        cls.campus = Campus.objects.create(
            name="Campus Central Lifecycle",
            slug="campus-lifecycle",
            geometry=poly
        )
        cls.building = Building.objects.create(
            campus=cls.campus,
            name="Edificio Lifecycle",
            code="ED-LIFE",
            geometry=poly
        )
        cls.floor = Floor.objects.create(
            building=cls.building,
            level=1,
            name="Planta Baja",
            geometry=poly
        )

    def setUp(self):
        super().setUp()

        file_obj = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='white')
        image.save(file_obj, 'PNG')
        file_obj.seek(0)

        self.plan_file = SimpleUploadedFile(
            "blueprint_test.png",
            file_obj.read(),
            content_type="image/png"
        )

        self.sample_proposal = {
            "spaces": [
                {
                    "name": "Aula 101 Integration",
                    "type": "CLASSROOM",
                    "coordinates": [[1.0, 1.0], [1.0, 5.0], [5.0, 5.0], [5.0, 1.0], [1.0, 1.0]]
                }
            ]
        }

    def test_full_spatial_plan_lifecycle_approval(self):
        """Flujo feliz completo: Subida -> Celery Eager -> Estado -> Aprobación -> Persistencia GIS."""
        # STEP 1: Subida de plano (POST /api/plans/upload/)
        upload_url = reverse('plan-upload')
        upload_payload = {
            'image': self.plan_file,
            'model_type': 'floor',
            'target_id': self.floor.id,
            'ai_provider': 'mock'
        }

        upload_response = self.client.post(upload_url, upload_payload, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_202_ACCEPTED)

        plan_id = upload_response.data['plan_id']

        # STEP 2: Verificación de Estado (procesado dinámicamente por Celery)
        status_url = reverse('plan-status', kwargs={'pk': plan_id})
        status_response = self.client.get(status_url)

        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status'], SpatialPlanStatus.REQUIRES_REVIEW)
        self.assertIsNotNone(status_response.data.get('intermediate_proposal'))

        # STEP 3: Aprobación del plano (POST /api/plans//approve/)
        approve_url = reverse('plan-approve', kwargs={'pk': plan_id})
        approve_response = self.client.post(
            approve_url,
            {'edited_draft_data': self.sample_proposal},
            format='json'
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)

        # STEP 4: Verificación GIS en Base de Datos
        plan = SpatialPlan.objects.get(id=plan_id)
        self.assertEqual(plan.status, SpatialPlanStatus.APPROVED)
        self.assertTrue(Space.objects.filter(floor=self.floor, name="Aula 101 Integration").exists())

    def test_full_spatial_plan_lifecycle_rejection(self):
        """Flujo alternativo: Subida -> Celery Eager -> Estado -> Rechazo -> Sin cambios en GIS."""
        # STEP 1: Subida de plano
        upload_url = reverse('plan-upload')
        upload_payload = {
            'image': self.plan_file,
            'model_type': 'floor',
            'target_id': self.floor.id,
            'ai_provider': 'mock'
        }

        upload_response = self.client.post(upload_url, upload_payload, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_202_ACCEPTED)

        plan_id = upload_response.data['plan_id']

        # STEP 2: Rechazo manual del plano (POST /api/plans//reject/)
        reject_url = reverse('plan-reject', kwargs={'pk': plan_id})
        rejection_reason = "Plano borroso, imposible determinar límites"
        reject_response = self.client.post(
            reject_url,
            {'reason': rejection_reason},
            format='json'
        )
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)

        # STEP 3: Verificación de Estado y de la Base de Datos GIS
        plan = SpatialPlan.objects.get(id=plan_id)
        self.assertEqual(plan.status, SpatialPlanStatus.REJECTED)
        self.assertIn(rejection_reason, str(plan.error_log))
        
        # Garantizar que no se insertó ninguna entidad en PostGIS tras el rechazo
        self.assertFalse(Space.objects.filter(floor=self.floor).exists())