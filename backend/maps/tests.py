import os
import json
import io
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Campus, Space, NavigationEdge
from .patterns import SpatialEntityFactory, ImportComposite, CampusImportStep, BuildingImportStep, FloorImportStep
from maps.models import Campus, Building, Floor, SpatialPlan, SpatialPlanStatus
from maps.tasks import process_spatial_plan_task



class GeoSpatialPipelineTestCase(APITestCase):
    """Suite de pruebas unitarias y de integración avanzada para la capa espacial de CampusNav3D."""

    def setUp(self):
        """Configuración inicial: Creamos un entorno base y un archivo JSON temporal para pruebas."""
        self.test_json_path = 'campus_test_fixtures.json'
        self.sample_data = {
            "campus": {
                "name": "Campus de Pruebas QA",
                "external_id": "CAMPUS-TEST-001",
                "geometry": "POLYGON ((-3.702 40.416, -3.704 40.416, -3.704 40.418, -3.702 40.418, -3.702 40.416))"
            },
            "building": {
                "name": "Edificio Gamma",
                "external_id": "BUILDING-TEST-001",
                "code": "ED-GAMMA",
                "geometry": "POLYGON ((-3.7025 40.4165, -3.7035 40.4165, -3.7035 40.4175, -3.7025 40.4175, -3.7025 40.4165))"
            },
            "floor": {
                "level": 1,
                "external_id": "FLOOR-TEST-001",
                "name": "Primera Planta",
                "altitude": 3.5,
                "geometry": "POLYGON ((-3.7025 40.4165, -3.7035 40.4165, -3.7035 40.4175, -3.7025 40.4175, -3.7025 40.4165))"
            },
            "spaces": [
                {
                    "external_id": "TEST-001",
                    "name": "Aula Magna",
                    "space_type": "CLASSROOM",
                    "geometry": "POLYGON ((-3.7026 40.4166, -3.7029 40.4166, -3.7029 40.4169, -3.7026 40.4169, -3.7026 40.4166))"
                },
                {
                    "external_id": "TEST-002",
                    "name": "Laboratorio de I+D",
                    "space_type": "LABORATORY",
                    "geometry": "POLYGON ((-3.7029 40.4166, -3.7034 40.4166, -3.7034 40.4169, -3.7029 40.4169, -3.7029 40.4166))"
                }
            ],
            "edges": [
                {
                    "name": "Camino Conector",
                    "source_external_id": "TEST-001",
                    "target_external_id": "TEST-002",
                    "geometry": "LINESTRING (-3.70275 40.41675, -3.70315 40.41675)"
                }
            ]
        }
        
        with open(self.test_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.sample_data, f)

    def tearDown(self):
        """Limpieza del entorno tras ejecutar los tests."""
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)

    def test_procedural_extractor_command(self):
        """Verifica que el ProceduralExtractor procesa el JSON e inyecta los modelos correctamente."""
        call_command('import_campus', self.test_json_path)

        self.assertEqual(Campus.objects.count(), 1)
        self.assertEqual(Space.objects.count(), 2)
        self.assertEqual(NavigationEdge.objects.count(), 1)

        aula_magna = Space.objects.get(external_id="TEST-001")
        self.assertEqual(aula_magna.geometry.geom_type, 'Polygon')
        self.assertEqual(len(aula_magna.geometry.coords[0]), 5)

    def test_factory_creates_explicit_entity_handlers(self):
        """Verifica que el factory expone un mecanismo explícito para crear handlers por tipo de entidad."""
        factory = SpatialEntityFactory()

        self.assertIsInstance(factory.create_handler('campus'), CampusImportStep)
        self.assertIsInstance(factory.create_handler('building'), BuildingImportStep)
        self.assertIsInstance(factory.create_handler('floor'), FloorImportStep)

        with self.assertRaises(ValueError):
            factory.create_handler('unknown')

    def test_composite_pipeline_executes_children_in_order(self):
        """Verifica que el composite ejecuta los pasos de importación de forma ordenada."""
        calls = []

        class RecordingStep:
            def __init__(self, name):
                self.name = name

            def process(self, payload, context):
                calls.append(self.name)
                context[self.name] = True

        pipeline = ImportComposite()
        pipeline.add(RecordingStep('campus'))
        pipeline.add(RecordingStep('building'))
        pipeline.process({}, {})

        self.assertEqual(calls, ['campus', 'building'])

    def test_api_geojson_output_format(self):
        """Verifica que los endpoints REST cumplen estrictamente con la especificación RFC 7946 (GeoJSON)."""
        call_command('import_campus', self.test_json_path)

        url = reverse('space-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        
        first_feature = data['features'][0]
        self.assertEqual(first_feature['type'], 'Feature')
        self.assertEqual(first_feature['geometry']['type'], 'Polygon')
        self.assertIn('name', first_feature['properties'])

    def test_extractor_rollback_on_corrupted_geometry(self):
        """
        [TEST DE ROBUSTEZ 1: ACID / Transaccionalidad]
        Verifica que si el pipeline de IA genera una geometría corrupta al final del 
        JSON, la base de datos realiza un ROLLBACK absoluto para evitar dejar datos huérfanos.
        """
        corrupted_json_path = 'campus_corrupted_test.json'
        corrupted_data = self.sample_data.copy()
        
        # Simulamos un fallo crítico de la IA inyectando un string de geometría totalmente roto
        corrupted_data['edges'][0]['geometry'] = "LINESTRING(NOT_A_VALID_COORDINATE_CORRUPTED)"

        with open(corrupted_json_path, 'w', encoding='utf-8') as f:
            json.dump(corrupted_data, f)

        try:
            # El cargador procedimental debe detectar el error de PostGIS y lanzar un CommandError
            with self.assertRaises(CommandError):
                call_command('import_campus', corrupted_json_path)
            
            # CONTROL DE CALIDAD: Aseguramos que la base de datos se mantiene virgen.
            # No debe haberse guardado absolutamente NADA del JSON, impidiendo datos corruptos parciales.
            self.assertEqual(Campus.objects.count(), 0)
            self.assertEqual(Space.objects.count(), 0)
            self.assertEqual(NavigationEdge.objects.count(), 0)
            
        finally:
            if os.path.exists(corrupted_json_path):
                os.remove(corrupted_json_path)

    def test_edge_topological_coherence_with_spaces(self):
        """
        [TEST DE ROBUSTEZ 2: Coherencia de Grafo IndoorGML]
        Verifica mediante los motores matemáticos de PostGIS que las aristas de navegación 
        no floten en el vacío, sino que conecten e intersecten físicamente con sus celdas de espacio.
        """
        # Inyectamos el campus sintético estructurado
        call_command('import_campus', self.test_json_path)

        # Recuperamos la arista del grafo dual
        edge = NavigationEdge.objects.first()

        # PostGIS analiza espacialmente si la línea cruza o toca los polígonos de las habitaciones
        intersects_source = edge.geometry.intersects(edge.source_space.geometry)
        intersects_target = edge.geometry.intersects(edge.target_space.geometry)

        # Si la IA pintara una arista fuera de la habitación, este assert tumbaría el test
        self.assertTrue(intersects_source, "ERROR CRÍTICO: La arista de navegación no intersecta con el espacio de origen.")
        self.assertTrue(intersects_target, "ERROR CRÍTICO: La arista de navegación no intersecta con el espacio de destino.")


    def test_factory_ocp_compliance(self):
        """Prueba que la fábrica puede expandirse en tiempo de ejecución sin modificarse."""
        from maps.factories import SpatialEntityFactory, BaseCreator
        
        # 1. Registrar una entidad ficticia al vuelo
        @SpatialEntityFactory.register('mock_zone')
        class MockZoneCreator(BaseCreator):
            @staticmethod
            def execute_creation(**kwargs):
                return "Entidad Extendida Exitosamente", True

        # 2. Invocar la creación sin haber tocado el core de la factoría
        result, created = SpatialEntityFactory.create('mock_zone')
        self.assertTrue(created)
        self.assertEqual(result, "Entidad Extendida Exitosamente")


#################### TEST SUITE DE INTEGRACIÓN PARA EL PIPELINE DE IA ####################
class SpatialPlanUploadTests(APITestCase):
    """Pruebas de integración para el endpoint de carga de planos (POST /api/plans/upload/)."""

    def setUp(self):
        """Creación de la estructura de datos previa para cada test."""
        self.campus = Campus.objects.create(
            name="Campus Central",
            slug="campus-central",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio A",
            code="ED-A",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor = Floor.objects.create(
            name="Planta Baja",
            level=0,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.upload_url = reverse('plan-upload')

    def _generate_dummy_image(self, name="test_plan.png", color="red"):
        """Función auxiliar para generar una imagen válida en memoria."""
        file_obj = io.BytesIO()
        img = Image.new('RGB', (100, 100), color=color)
        img.save(file_obj, 'PNG')
        file_obj.seek(0)
        return SimpleUploadedFile(name, file_obj.read(), content_type='image/png')

    def test_upload_spatial_plan_success(self):
        """1.1 Verifica la subida exitosa de un plano y el disparo asíncrono sincrónico (Eager)."""
        image = self._generate_dummy_image("floor_plan.png", color="blue")
        data = {
            'image': image,
            'model_type': 'floor',
            'target_id': self.floor.id,
            'ai_provider': 'mock'
        }

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('plan_id', response.data)

        plan_id = response.data['plan_id']
        plan = SpatialPlan.objects.get(id=plan_id)

        # Verificación de asociación polimórfica (GenericForeignKey)
        floor_content_type = ContentType.objects.get_for_model(Floor)
        self.assertEqual(plan.content_type, floor_content_type)
        self.assertEqual(plan.object_id, self.floor.id)
        self.assertIsNotNone(plan.file_hash)

        # Dado que CELERY_TASK_ALWAYS_EAGER=True, la tarea se ejecuta de inmediato:
        # Pasa de UPLOADED -> PREPROCESSING -> EXTRACTING -> REQUIRES_REVIEW
        self.assertEqual(plan.status, SpatialPlanStatus.REQUIRES_REVIEW)
        self.assertIsNotNone(plan.intermediate_proposal)

    def test_upload_invalid_target_or_model(self):
        """1.2 Verifica error HTTP 400 al enviar modelo no reconocido o target_id inexistente."""
        # Caso A: Modelo objetivo no válido
        image1 = self._generate_dummy_image("test.png")

        data_bad_model = {
            'image': image1,
            'model_type': 'modelo_inexistente',
            'target_id': self.floor.id
        }
        res_bad_model = self.client.post(self.upload_url, data_bad_model, format='multipart')
        self.assertEqual(res_bad_model.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('model_type', res_bad_model.data)

        # Caso B: ID objetivo que no existe en la base de datos
        image2 = self._generate_dummy_image("test.png")

        data_bad_target = {
            'image': image2,
            'model_type': 'floor',
            'target_id': 99999
        }
        res_bad_target = self.client.post(self.upload_url, data_bad_target, format='multipart')
        self.assertEqual(res_bad_target.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_id', res_bad_target.data)

    def test_upload_duplicate_entity_prevention(self):
        """1.3 Verifica que no se permita subir un segundo plano a una entidad que ya posee uno."""
        image1 = self._generate_dummy_image("plan1.png", color="green")
        data1 = {
            'image': image1,
            'model_type': 'floor',
            'target_id': self.floor.id
        }
        res1 = self.client.post(self.upload_url, data1, format='multipart')
        self.assertEqual(res1.status_code, status.HTTP_202_ACCEPTED)

        # Intento de re-asociar un nuevo plano a la misma planta
        image2 = self._generate_dummy_image("plan2.png", color="yellow")
        data2 = {
            'image': image2,
            'model_type': 'floor',
            'target_id': self.floor.id
        }
        res2 = self.client.post(self.upload_url, data2, format='multipart')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_id', res2.data)

    def test_upload_duplicate_file_hash_prevention(self):
        """1.4 Verifica el rechazo de archivos duplicados mediante el hash SHA-256."""
        # Creamos una segunda planta para aislar la prueba de duplicación de entidad
        floor2 = Floor.objects.create(
            name="Planta Alta",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )

        file_obj = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='cyan')
        img.save(file_obj, 'PNG')
        image_bytes = file_obj.getvalue()

        file1 = SimpleUploadedFile("imagen1.png", image_bytes, content_type="image/png")
        data1 = {
            'image': file1,
            'model_type': 'floor',
            'target_id': self.floor.id
        }
        res1 = self.client.post(self.upload_url, data1, format='multipart')
        self.assertEqual(res1.status_code, status.HTTP_202_ACCEPTED)

        # Intentamos subir exactamente los mismos bytes a floor2
        file2 = SimpleUploadedFile("imagen1_renombrada.png", image_bytes, content_type="image/png")
        data2 = {
            'image': file2,
            'model_type': 'floor',
            'target_id': floor2.id
        }
        res2 = self.client.post(self.upload_url, data2, format='multipart')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', res2.data)

class SpatialPlanTaskTests(TestCase):
    """Pruebas de integración para la tarea asíncrona de Celery (process_spatial_plan_task)."""

    def setUp(self):
        """Creación del objeto SpatialPlan base en estado UPLOADED."""
        self.campus = Campus.objects.create(
            name="Campus Norte",
            slug="campus-norte",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio B",
            code="ED-B",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor = Floor.objects.create(
            name="Planta 1",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        
        floor_content_type = ContentType.objects.get_for_model(Floor)
        self.plan = SpatialPlan.objects.create(
            content_type=floor_content_type,
            object_id=self.floor.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="dummy_hash_for_task_testing_123"
        )

    def test_process_spatial_plan_task_success(self):
        """2.1 Verifica el ciclo completo de procesamiento con MockProceduralAdapter."""
        # Ejecutamos la tarea pasándole el ID del plano
        process_spatial_plan_task(self.plan.id, provider_name='mock')

        # Recargamos la instancia desde PostgreSQL
        self.plan.refresh_from_db()

        # Verificamos que avanzó hasta REQUIRES_REVIEW
        self.assertEqual(self.plan.status, SpatialPlanStatus.REQUIRES_REVIEW)

        # Verificamos que intermediate_proposal contiene la estructura de espacios
        self.assertIsNotNone(self.plan.intermediate_proposal)
        self.assertIn('spaces', self.plan.intermediate_proposal)
        self.assertGreater(len(self.plan.intermediate_proposal['spaces']), 0)

        # Verificamos que se asignaron metadatos de IA
        self.assertIsNotNone(self.plan.ai_metadata)

    def test_process_spatial_plan_task_not_found(self):
        """2.2 Verifica el comportamiento si el plan_id no existe en la base de datos."""
        invalid_id = 99999
        
        # Debe capturar DoesNotExist internamente y retornar sin lanzar una excepción sin controlar
        try:
            process_spatial_plan_task(invalid_id, provider_name='mock')
        except Exception as e:
            self.fail(f"La tarea lanzó una excepción inesperada para un ID inexistente: {e}")

    @patch('maps.providers.mock.MockProceduralAdapter.extract_layout')
    def test_process_spatial_plan_task_failure_transitions_to_failed(self, mock_extract):
        """2.3 Verifica que ante un fallo en el adaptador, el plano pase a estado FAILED."""
        # Simulamos un error en la extracción del adaptador
        mock_extract.side_effect = Exception("Error simulado de extracción por IA")

        # Invocamos la tarea sin reintentos automáticos en el test para evaluar la transición
        with patch.object(process_spatial_plan_task, 'retry', side_effect=Exception("Task Retry Triggered")):
            with self.assertRaises(Exception):
                process_spatial_plan_task(self.plan.id, provider_name='mock')

        self.plan.refresh_from_db()
        self.assertEqual(self.plan.status, SpatialPlanStatus.FAILED)
        self.assertIn("Error simulado de extracción por IA", str(self.plan.error_log))

class SpatialPlanQueryTests(APITestCase):
    """Pruebas de integración para endpoints de consulta (GET /api/plans/ y GET /api/plans/<id>/status/)."""

    def setUp(self):
        """Configuración del entorno de prueba con entidades base y planos en diferentes estados."""
        self.campus = Campus.objects.create(
            name="Campus Sur",
            slug="campus-sur",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio C",
            code="ED-C",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor1 = Floor.objects.create(
            name="Planta 1",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor2 = Floor.objects.create(
            name="Planta 2",
            level=2,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )

        self.floor_ct = ContentType.objects.get_for_model(Floor)

        # Plano 1: En estado REQUIRES_REVIEW con propuesta de IA
        self.plan_requires_review = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor1.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_query_test_1",
            intermediate_proposal={
                "spaces": [
                    {
                        "name": "Aula 101",
                        "type": "CLASSROOM",
                        "coordinates": [[0.0, 0.0], [0.0, 5.0], [5.0, 5.0], [5.0, 0.0], [0.0, 0.0]]
                    }
                ]
            },
            ai_metadata={"provider": "mock", "confidence": 0.95}
        )

        # Plano 2: En estado APPROVED
        self.plan_approved = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor2.id,
            status=SpatialPlanStatus.APPROVED,
            file_hash="hash_query_test_2"
        )

    def test_get_plan_status_success(self):
        """3.1 Verifica la obtención exitosa del estado y propuesta JSON de un plano."""
        url = reverse('plan-status', kwargs={'pk': self.plan_requires_review.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], SpatialPlanStatus.REQUIRES_REVIEW)
        self.assertIn('intermediate_proposal', response.data)
        self.assertEqual(
            response.data['intermediate_proposal']['spaces'][0]['name'],
            "Aula 101"
        )
        self.assertIn('ai_metadata', response.data)

    def test_get_plan_status_not_found(self):
        """3.2 Verifica devuelvan HTTP 404 al consultar un ID de plano inexistente."""
        invalid_url = reverse('plan-status', kwargs={'pk': 99999})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_spatial_plans(self):
        """3.3 Verifica que el endpoint de listado GET /api/plans/ retorne todos los planos registrados."""
        list_url = reverse('spatialplan-list')
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debe incluir los 2 planos creados en el setUp
        results = response.data
        self.assertEqual(len(results), 2)

        # Verificamos que contenga las claves principales esperadas
        first_item = results[0]
        self.assertIn('id', first_item)
        self.assertIn('status', first_item)
        self.assertIn('file_hash', first_item)
        self.assertIn('created_at', first_item)

class SpatialPlanApproveTests(APITestCase):
    """Pruebas de integración para la aprobación de planos y persistencia GIS (POST /api/plans/<id>/approve/)."""

    def setUp(self):
        """Creación de la estructura base y un plano listo para revisión."""
        self.campus = Campus.objects.create(
            name="Campus Este",
            slug="campus-este",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio D",
            code="ED-D",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor = Floor.objects.create(
            name="Planta 1",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor_ct = ContentType.objects.get_for_model(Floor)

        # Propuesta válida generada previamente
        self.valid_proposal = {
            "spaces": [
                {
                    "name": "Aula 201",
                    "type": "CLASSROOM",
                    "coordinates": [[1.0, 1.0], [1.0, 4.0], [4.0, 4.0], [4.0, 1.0], [1.0, 1.0]]
                },
                {
                    "name": "Pasillo Central",
                    "type": "CORRIDOR",
                    "coordinates": [[4.0, 1.0], [4.0, 4.0], [6.0, 4.0], [6.0, 1.0], [4.0, 1.0]]
                }
            ]
        }

        self.plan_review = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_approve_test_123",
            intermediate_proposal=self.valid_proposal
        )

    def test_approve_plan_using_ai_proposal(self):
        """4.1 Verifica la aprobación usando la propuesta de IA por defecto y creación de objetos Space en PostGIS."""
        url = reverse('plan-approve', kwargs={'pk': self.plan_review.id})
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.plan_review.refresh_from_db()
        self.assertEqual(self.plan_review.status, SpatialPlanStatus.APPROVED)

        # Verificar que se crearon los 2 recintos asociados a la planta en PostGIS
        spaces = Space.objects.filter(floor=self.floor)
        self.assertEqual(spaces.count(), 2)

        space_names = list(spaces.values_list('name', flat=True))
        self.assertIn("Aula 201", space_names)
        self.assertIn("Pasillo Central", space_names)

    def test_approve_plan_with_edited_draft_data(self):
        """4.2 Verifica que los datos editados por el usuario prevalecen sobre la propuesta original."""
        url = reverse('plan-approve', kwargs={'pk': self.plan_review.id})
        
        edited_payload = {
            "edited_draft_data": {
                "spaces": [
                    {
                        "name": "Laboratorio de Robótica (Editado)",
                        "type": "LAB",
                        "coordinates": [[1.0, 1.0], [1.0, 5.0], [5.0, 5.0], [5.0, 1.0], [1.0, 1.0]]
                    }
                ]
            }
        }

        response = self.client.post(url, edited_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.plan_review.refresh_from_db()
        self.assertEqual(self.plan_review.status, SpatialPlanStatus.APPROVED)

        # Solo debe existir 1 recinto con el nombre editado
        spaces = Space.objects.filter(floor=self.floor)
        self.assertEqual(spaces.count(), 1)
        self.assertEqual(spaces.first().name, "Laboratorio de Robótica (Editado)")

    def test_approve_plan_invalid_status(self):
        """4.3 Verifica error HTTP 400 al intentar aprobar planos en estado UPLOADED o APPROVED."""
        # Creamos una planta auxiliar para no violar el UNIQUE constraint
        floor_uploaded = Floor.objects.create(
            name="Planta Auxiliar Uploaded",
            level=2,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )

        plan_uploaded = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=floor_uploaded.id,
            status=SpatialPlanStatus.UPLOADED,
            file_hash="hash_uploaded_test"
        )

        url = reverse('plan-approve', kwargs={'pk': plan_uploaded.id})
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_approve_plan_empty_spaces_rejection(self):
        """4.4 Verifica que se rechace la aprobación de propuestas que contengan cero recintos."""
        # Creamos una planta auxiliar para no violar el UNIQUE constraint
        floor_empty = Floor.objects.create(
            name="Planta Auxiliar Vacía",
            level=3,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )

        plan_empty = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=floor_empty.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_empty_spaces",
            intermediate_proposal={"spaces": []}
        )

        url = reverse('plan-approve', kwargs={'pk': plan_empty.id})
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('maps.models.Space.objects.create')
    def test_approve_plan_atomic_transaction_rollback(self, mock_space_create):
        """4.5 Verifica que un error a mitad de inserción haga rollback completo (0 espacios creados y estado intacto)."""
        # Forzamos que la primera creación de Space lance una excepción
        mock_space_create.side_effect = Exception("Fallo simulado en PostGIS/Database")

        url = reverse('plan-approve', kwargs={'pk': self.plan_review.id})
        
        response = self.client.post(url, {}, format='json')

        # DRF debe retornar un código de error HTTP 500 o 400
        self.assertIn(response.status_code, [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_400_BAD_REQUEST])

        # Verificación del Rollback: Estado intacto y cero espacios creados
        self.plan_review.refresh_from_db()
        self.assertEqual(self.plan_review.status, SpatialPlanStatus.REQUIRES_REVIEW)
        self.assertEqual(Space.objects.filter(floor=self.floor).count(), 0)

class SpatialPlanRejectTests(APITestCase):
    """Pruebas de integración para el rechazo manual de planos (POST /api/plans/<id>/reject/)."""

    def setUp(self):
        """Creación de la estructura base y plantas aisladas para evitar violar restricciones UNIQUE."""
        self.campus = Campus.objects.create(
            name="Campus Oeste",
            slug="campus-oeste",
            geometry=Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        )
        self.building = Building.objects.create(
            name="Edificio E",
            code="ED-E",
            campus=self.campus,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor1 = Floor.objects.create(
            name="Planta 1",
            level=1,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor2 = Floor.objects.create(
            name="Planta 2",
            level=2,
            building=self.building,
            geometry=Polygon(((1, 1), (1, 9), (9, 9), (9, 1), (1, 1)))
        )
        self.floor_ct = ContentType.objects.get_for_model(Floor)

        # Plano 1: Estado REQUIRES_REVIEW listo para ser rechazado
        self.plan_review = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor1.id,
            status=SpatialPlanStatus.REQUIRES_REVIEW,
            file_hash="hash_reject_test_1"
        )

    def test_reject_plan_success(self):
        """5.1 Verifica que un plano en REQUIRES_REVIEW pueda ser rechazado guardando la razón en error_log."""
        url = reverse('plan-reject', kwargs={'pk': self.plan_review.id})
        reason = "Ilegible: Las paredes de la zona este no están claras"
        
        response = self.client.post(url, {'reason': reason}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.plan_review.refresh_from_db()
        self.assertEqual(self.plan_review.status, SpatialPlanStatus.REJECTED)
        self.assertIn(reason, str(self.plan_review.error_log))

    def test_reject_plan_invalid_status(self):
        """5.2 Verifica error HTTP 400 al intentar rechazar un plano que ya está en estado APPROVED."""
        plan_approved = SpatialPlan.objects.create(
            content_type=self.floor_ct,
            object_id=self.floor2.id,
            status=SpatialPlanStatus.APPROVED,
            file_hash="hash_reject_test_2"
        )

        url = reverse('plan-reject', kwargs={'pk': plan_approved.id})
        response = self.client.post(url, {'reason': "Ya no me gusta"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        plan_approved.refresh_from_db()
        # El estado debe mantenerse intacto
        self.assertEqual(plan_approved.status, SpatialPlanStatus.APPROVED)