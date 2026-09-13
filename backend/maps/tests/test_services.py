from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon

from maps.models import Campus, Building, Floor, SpatialPlan, SpatialPlanStatus, Space
from maps.services import PlanService, ApprovalService, IngestionService


class ServiceLayerTestCase(TestCase):
    """Pruebas unitarias aisladas para la capa de servicios del dominio (services/)."""

    def setUp(self):
        self.campus = Campus.objects.create(
            name="Campus Service Test",
            slug="campus-service-test",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio S",
            code="ED-S",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor = Floor.objects.create(
            name="Planta 1 Service",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor_ct = ContentType.objects.get_for_model(Floor)

        self.valid_proposal = {
            "spaces": [
                {
                    "name": "Despacho S1",
                    "type": "OFFICE",
                    "coordinates": [[1.0, 1.0], [1.0, 3.0], [3.0, 3.0], [3.0, 1.0], [1.0, 1.0]]
                }
            ]
        }

    # -------------------------------------------------------------------------
    # PlanService Tests
    # -------------------------------------------------------------------------

    @patch('maps.tasks.process_spatial_plan_task.delay')
    def test_plan_service_upload_and_enqueue(self, mock_task_delay):
        """Verifica la persistencia de un plano y el encolado de la tarea asíncrona."""
        mock_serializer = MagicMock()
        mock_serializer.validated_data = {
            'ai_provider': 'mock',
            'content_type': self.floor_ct,
            'target_id': self.floor.id
        }
        
        created_plan = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="hash_service_test_1"
        )
        mock_serializer.save.return_value = created_plan

        result = PlanService.upload_and_enqueue_plan(mock_serializer)

        self.assertEqual(result, created_plan)
        mock_task_delay.assert_called_once_with(created_plan.id, provider_name='mock')

    def test_plan_service_reject_plan_invalid_status_raises_error(self):
        """Verifica que intentar rechazar un plano fuera de REQUIRES_REVIEW lance ValueError."""
        plan_uploaded = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="hash_service_reject_invalid"
        )

        with self.assertRaises(ValueError):
            PlanService.reject_plan(plan_uploaded.id, reason="Razon cualquiera")

    # -------------------------------------------------------------------------
    # ApprovalService Tests
    # -------------------------------------------------------------------------

    def test_approval_service_approve_plan_success(self):
        """Verifica la aprobación directa a través del servicio y creación de entidades Space."""
        plan_review = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_approval_service_1",
            intermediate_proposal=self.valid_proposal
        )

        approved_plan, created_spaces = ApprovalService.approve_plan(plan_review.id)

        self.assertEqual(approved_plan.status, SpatialPlanStatus.APPROVED)
        self.assertEqual(len(created_spaces), 1)
        self.assertEqual(Space.objects.filter(floor=self.floor).count(), 1)
        self.assertEqual(Space.objects.first().name, "Despacho S1")

    def test_approval_service_approve_empty_proposal_raises_error(self):
        """Verifica que aprobar una propuesta vacía lance ValueError en la capa de servicio."""
        plan_empty = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_approval_empty",
            intermediate_proposal={"spaces": []}
        )

        with self.assertRaises(ValueError):
            ApprovalService.approve_plan(plan_empty.id)

    # -------------------------------------------------------------------------
    # IngestionService Tests
    # -------------------------------------------------------------------------

    def test_ingestion_service_process_plan_success(self):
        """Verifica el procesamiento directo de ingesta en el servicio."""
        plan = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="hash_ingestion_service_1"
        )

        processed_plan = IngestionService.process_plan(plan.id, provider_name='mock')

        self.assertEqual(processed_plan.status, SpatialPlanStatus.REQUIRES_REVIEW)
        self.assertIsNotNone(processed_plan.intermediate_proposal)
        self.assertIsNotNone(processed_plan.ai_metadata)

    def test_ingestion_service_non_existent_plan_returns_none(self):
        """Verifica que pasar un ID inexistente retorne None sin romper la aplicación."""
        result = IngestionService.process_plan(99999)
        self.assertIsNone(result)

    @patch('maps.providers.mock.MockProceduralAdapter.extract_layout')
    def test_ingestion_service_failure_transitions_to_failed(self, mock_extract):
        """Verifica que si la extracción falla, la máquina de estados pase a FAILED."""
        plan = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="hash_ingestion_fail"
        )
        mock_extract.side_effect = Exception("Fallo forzado en adaptador IA")

        with self.assertRaises(Exception):
            IngestionService.process_plan(plan.id)

        plan.refresh_from_db()
        self.assertEqual(plan.status, SpatialPlanStatus.FAILED)
        self.assertIn("Fallo forzado en adaptador IA", str(plan.error_log))