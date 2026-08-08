import networkx as nx
from django.test import TestCase
from django.contrib.gis.geos import Polygon, LineString

from maps.models import Campus, Building, Floor, Space, NavigationEdge
from maps.graph_builder import GraphBuilder


class GraphBuilderTestCase(TestCase):
    """
    Suite de pruebas para el constructor de grafos (GraphBuilder),
    encargado de transformar la red de navegación de PostGIS en un objeto NetworkX.
    """

    @classmethod
    def setUpTestData(cls):
        """Optimización: Fixtures de PostGIS persistidos una sola vez para toda la clase."""
        cls.campus = Campus.objects.create(
            name="Campus Central Test",
            slug="campus-central-test",
            geometry=Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
        )
        cls.building = Building.objects.create(
            campus=cls.campus,
            name="Edificio de Innovación",
            code="ED-INV",
            geometry=Polygon(((5, 5), (5, 45), (45, 45), (45, 5), (5, 5)))
        )
        cls.floor = Floor.objects.create(
            building=cls.building,
            level=0,
            name="Planta Baja",
            geometry=Polygon(((5, 5), (5, 45), (45, 45), (45, 5), (5, 5)))
        )

        # Creación de espacios (Nodos)
        cls.space_a = Space.objects.create(
            floor=cls.floor,
            name="Entrada Principal",
            space_type="HALL",
            geometry=Polygon(((10, 10), (10, 15), (15, 15), (15, 10), (10, 10)))
        )
        cls.space_b = Space.objects.create(
            floor=cls.floor,
            name="Pasillo Central",
            space_type="CORRIDOR",
            geometry=Polygon(((15, 10), (15, 15), (25, 15), (25, 10), (15, 10)))
        )
        cls.space_c = Space.objects.create(
            floor=cls.floor,
            name="Escalera A",
            space_type="STAIRS",
            geometry=Polygon(((25, 10), (25, 15), (30, 15), (30, 10), (25, 10)))
        )
        cls.space_isolated = Space.objects.create(
            floor=cls.floor,
            name="Almacén Aislado",
            space_type="ROOM",
            geometry=Polygon(((40, 40), (40, 45), (45, 45), (45, 40), (40, 40)))
        )

        # Creación de aristas de navegación (Edges)
        cls.edge_a_b = NavigationEdge.objects.create(
            name="E-AB",
            source_space=cls.space_a,
            target_space=cls.space_b,
            geometry=LineString((12.5, 12.5), (20.0, 12.5)),
            is_accessible=True
        )
        cls.edge_b_c = NavigationEdge.objects.create(
            name="E-BC",
            source_space=cls.space_b,
            target_space=cls.space_c,
            geometry=LineString((20.0, 12.5), (27.5, 12.5)),
            is_accessible=False  # No accesible para PMR por ser escalera
        )

        # [CASO LÍMITE] Arista autorreferencial (Bucle)
        cls.edge_loop = NavigationEdge.objects.create(
            name="E-LOOP-A",
            source_space=cls.space_a,
            target_space=cls.space_a,
            geometry=LineString((12.5, 12.5), (13.0, 13.0), (12.5, 12.5)),
            is_accessible=True
        )

    def test_build_graph_returns_networkx_graph_instance(self):
        """Verifica que GraphBuilder.build_graph() retorne un objeto válido de NetworkX."""
        graph = GraphBuilder.build_graph()
        self.assertIsInstance(graph, (nx.Graph, nx.DiGraph))

    def test_graph_contains_all_nodes_including_isolated(self):
        """Verifica que todos los espacios de la BDD se registren como nodos en el grafo."""
        graph = GraphBuilder.build_graph()

        self.assertIn(self.space_a.id, graph.nodes)
        self.assertIn(self.space_b.id, graph.nodes)
        self.assertIn(self.space_c.id, graph.nodes)
        self.assertIn(self.space_isolated.id, graph.nodes)

    def test_graph_edges_and_attributes(self):
        """Verifica la existencia de conexiones y la correcta asignación de atributos de arista."""
        graph = GraphBuilder.build_graph()

        self.assertTrue(graph.has_edge(self.space_a.id, self.space_b.id))
        
        edge_data = graph[self.space_a.id][self.space_b.id]
        
        # Si es un MultiGraph o DiGraph, extraemos el primer diccionario de datos
        if 0 in edge_data:
            edge_data = edge_data[0]

        self.assertIn('weight', edge_data)
        self.assertIn('is_accessible', edge_data)
        self.assertTrue(edge_data['is_accessible'])
        self.assertGreater(edge_data['weight'], 0.0)

    def test_graph_builder_handles_self_referential_loops(self):
        """
        [CASO LÍMITE]
        Verifica que una arista donde source_space == target_space no rompa
        la construcción del grafo ni cause recursión infinita.
        """
        graph = GraphBuilder.build_graph()
        
        self.assertTrue(graph.has_edge(self.space_a.id, self.space_a.id))
        
        # El nodo desconectado no debe tener aristas hacia sí mismo ni hacia otros
        self.assertEqual(graph.degree(self.space_isolated.id), 0)

    def test_graph_builder_floor_filtering(self):
        """Verifica que la construcción del grafo permita filtrar por planta específica si el parámetro existe."""
        if hasattr(GraphBuilder, 'build_graph_for_floor'):
            graph_floor = GraphBuilder.build_graph_for_floor(self.floor.id)
            self.assertIn(self.space_a.id, graph_floor.nodes)
            self.assertIn(self.space_b.id, graph_floor.nodes)