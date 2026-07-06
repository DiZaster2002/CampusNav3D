import os
import json
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Campus, Space, NavigationEdge
from .patterns import SpatialEntityFactory, ImportComposite, CampusImportStep, BuildingImportStep, FloorImportStep

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