from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Polygon, LineString
from rest_framework import status

from maps.models import Campus, Building, Floor, Space, NavigationEdge
from .base import AuthenticatedAPITestCase
from maps.graph_builder import GraphBuilder
from maps.routing_strategies import FastestPathStrategy, AccessiblePathStrategy
from maps.navigation_facade import NavigationFacade


class RoutingModuleTestCase(AuthenticatedAPITestCase):
    """
    Suite de pruebas unitarias y de integración para las estrategias de cálculo
    de rutas, la fachada de navegación y los endpoints de itinerario.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Configuración optimizada de topología espacial:
        Ruta A (Rápida): S1 -> S2 (Escalera, No Accesible) -> S4
        Ruta B (Accesible): S1 -> S3 (Rampa, Accesible) -> S4
        Nodo Aislado: S5
        """
        cls.campus = Campus.objects.create(
            name='Campus Central Routing',
            slug='campus-routing',
            geometry=Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0)))
        )
        cls.building = Building.objects.create(
            campus=cls.campus,
            name='Edificio de Pruebas',
            code='ED-ROUTING',
            geometry=Polygon(((10, 10), (10, 90), (90, 90), (90, 10), (10, 10)))
        )
        cls.floor = Floor.objects.create(
            building=cls.building,
            level=0,
            name='Planta Baja',
            geometry=Polygon(((10, 10), (10, 90), (90, 90), (90, 10), (10, 10)))
        )

        cls.s1 = Space.objects.create(
            floor=cls.floor, name='Origen', space_type='CORRIDOR',
            geometry=Polygon(((10, 10), (10, 20), (20, 20), (20, 10), (10, 10)))
        )
        cls.s2 = Space.objects.create(
            floor=cls.floor, name='Escalera (Rápida)', space_type='STAIRS',
            geometry=Polygon(((20, 10), (20, 20), (30, 20), (30, 10), (20, 10)))
        )
        cls.s3 = Space.objects.create(
            floor=cls.floor, name='Rampa PMR (Accesible)', space_type='CORRIDOR',
            geometry=Polygon(((10, 20), (10, 30), (20, 30), (20, 20), (10, 20)))
        )
        cls.s4 = Space.objects.create(
            floor=cls.floor, name='Destino', space_type='ROOM',
            geometry=Polygon(((30, 10), (30, 20), (40, 20), (40, 10), (30, 10)))
        )
        cls.s5_isolated = Space.objects.create(
            floor=cls.floor, name='Espacio Desconectado', space_type='ROOM',
            geometry=Polygon(((80, 80), (80, 90), (90, 90), (90, 80), (80, 80)))
        )

        # Aristas: Ruta corta inaccesible por escaleras
        NavigationEdge.objects.create(
            name='E1-2', source_space=cls.s1, target_space=cls.s2,
            geometry=LineString((15, 15), (25, 15)), is_accessible=False
        )
        NavigationEdge.objects.create(
            name='E2-4', source_space=cls.s2, target_space=cls.s4,
            geometry=LineString((25, 15), (35, 15)), is_accessible=True
        )

        # Aristas: Ruta mas larga accesible por rampa
        NavigationEdge.objects.create(
            name='E1-3', source_space=cls.s1, target_space=cls.s3,
            geometry=LineString((15, 15), (15, 25)), is_accessible=True
        )
        NavigationEdge.objects.create(
            name='E3-4', source_space=cls.s3, target_space=cls.s4,
            geometry=LineString((15, 25), (35, 15)), is_accessible=True
        )

    def test_fastest_path_strategy_selects_shortest_route(self):
        """Verifica que la estrategia rápida elija el camino por escaleras (S1 -> S2 -> S4)."""
        graph = GraphBuilder.build_graph()
        strategy = FastestPathStrategy()
        
        result = strategy.calculate_route(graph, self.s1.id, self.s4.id)

        self.assertEqual(result['path'], [self.s1.id, self.s2.id, self.s4.id])
        self.assertNotIn('error', result)
        self.assertGreater(result['total_distance'], 0.0)

    def test_accessible_path_strategy_avoids_inaccessible_edges(self):
        """Verifica que la estrategia accesible evite escaleras y use la rampa (S1 -> S3 -> S4)."""
        graph = GraphBuilder.build_graph()
        strategy = AccessiblePathStrategy()

        result = strategy.calculate_route(graph, self.s1.id, self.s4.id)

        self.assertEqual(result['path'], [self.s1.id, self.s3.id, self.s4.id])
        self.assertNotIn(self.s2.id, result['path'])

    def test_same_source_and_target_returns_zero_distance(self):
        """[CASO LÍMITE] Verifica que pedir origen == destino retorne distancia 0.0 e itinerario trivial."""
        graph = GraphBuilder.build_graph()
        strategy = FastestPathStrategy()

        result = strategy.calculate_route(graph, self.s1.id, self.s1.id)

        self.assertEqual(result['path'], [self.s1.id])
        self.assertEqual(result['total_distance'], 0.0)

    def test_unreachable_node_returns_error_response(self):
        """[CASO LÍMITE] Verifica la respuesta adecuada cuando no hay camino conexo hacia el destino."""
        graph = GraphBuilder.build_graph()
        strategy = FastestPathStrategy()

        result = strategy.calculate_route(graph, self.s1.id, self.s5_isolated.id)

        self.assertEqual(result['path'], [])
        self.assertIn('error', result)

    def test_navigation_facade_integration(self):
        """Verifica que NavigationFacade orqueste correctamente la selección de estrategia."""
        facade = NavigationFacade()

        # Ruta estándar / rápida
        fast_route = facade.get_route(self.s1.id, self.s4.id, preference='fastest')
        self.assertEqual(fast_route['path'], [self.s1.id, self.s2.id, self.s4.id])

        # Ruta adaptada PMR
        accessible_route = facade.get_route(self.s1.id, self.s4.id, preference='accessible')
        self.assertEqual(accessible_route['path'], [self.s1.id, self.s3.id, self.s4.id])

    def test_routing_api_endpoint_success(self):
        """Verifica el endpoint REST GET /api/route/ con parámetros válidos."""
        url = reverse('navigation-route')
        params = {
            'start_space_id': self.s1.id,
            'target_space_id': self.s4.id,
            'preference': 'accessible'
        }

        response = self.client.get(url, params, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('path', response.data)
        self.assertIn('total_distance', response.data)
        self.assertEqual(response.data['path'], [self.s1.id, self.s3.id, self.s4.id])